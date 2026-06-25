from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, ConfigDict

from src.models.world import WorldState


class OrderType(str):
    BID = "bid"
    ASK = "ask"


class TradeStatus(str):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


@dataclass
class Order:
    order_id: str
    agent_id: str
    order_type: str
    price: float
    quantity: float
    timestamp: float
    metadata: dict = field(default_factory=dict)


@dataclass
class Trade:
    trade_id: str
    buyer_id: str
    seller_id: str
    price: float
    quantity: float
    timestamp: float
    status: str = TradeStatus.PENDING
    metadata: dict = field(default_factory=dict)


class OrderBook(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bids: list[Order] = Field(default_factory=list)
    asks: list[Order] = Field(default_factory=list)
    last_clearing_price: float = 0.0
    market_depth: float = 0.0


class Portfolio(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str
    cash: float = 10000.0
    resources: dict[str, float] = Field(default_factory=dict)
    trade_history: list[dict[str, Any]] = Field(default_factory=list)
    infrastructure_level: float = 0.0

    def adjust_balance(self, resource: str, delta: float) -> None:
        current = self.resources.get(resource, 0.0)
        self.resources[resource] = current + delta

    def record_trade(self, trade: dict[str, Any]) -> None:
        self.trade_history.append(trade)


class MarketState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_price: float = 0.0
    last_update: float = 0.0
    order_book: OrderBook = Field(default_factory=OrderBook)
    yields: dict[str, float] = Field(default_factory=dict)
    liquidity: dict[str, float] = Field(default_factory=dict)
    price_history: list[float] = Field(default_factory=list)


class EconomyEngine:
    def __init__(self, world_state: WorldState | None = None):
        self.world_state = world_state or WorldState()
        self.market_state = MarketState()
        self.agent_portfolios: dict[str, Portfolio] = {}

    def place_bid(self, agent_id: str, price: float, quantity: float, resource: str = "default") -> dict[str, Any]:
        if agent_id not in self.world_state.agents:
            return {"status": TradeStatus.REJECTED, "reason": "agent_not_found"}

        portfolio = self._get_portfolio(agent_id)
        required_cash = price * quantity
        if required_cash > portfolio.cash:
            return {
                "status": TradeStatus.REJECTED,
                "reason": "insufficient_margin",
                "required": required_cash,
                "available": portfolio.cash,
            }

        order = Order(
            order_id=f"bid-{time.time()}",
            agent_id=agent_id,
            order_type="bid",
            price=price,
            quantity=quantity,
            timestamp=time.time(),
            metadata={"resource": resource},
        )
        self.market_state.order_book.bids.append(order)
        return {"status": "accepted", "order_id": order.order_id, "side": "bid", "price": price, "quantity": quantity}

    def place_ask(self, agent_id: str, price: float, quantity: float, resource: str = "default") -> dict[str, Any]:
        if agent_id not in self.world_state.agents:
            return {"status": TradeStatus.REJECTED, "reason": "agent_not_found"}

        portfolio = self._get_portfolio(agent_id)
        available = portfolio.resources.get(resource, 0.0)
        if quantity > available:
            return {
                "status": TradeStatus.REJECTED,
                "reason": "insufficient_resource",
                "required": quantity,
                "available": available,
            }

        order = Order(
            order_id=f"ask-{time.time()}",
            agent_id=agent_id,
            order_type="ask",
            price=price,
            quantity=quantity,
            timestamp=time.time(),
            metadata={"resource": resource},
        )
        self.market_state.order_book.asks.append(order)
        return {"status": "accepted", "order_id": order.order_id, "side": "ask", "price": price, "quantity": quantity}

    def match_orders(self, clearing_mechanism: str = "continuous") -> list[Trade]:
        self.market_state.order_book.asks.sort(key=lambda o: (o.price, o.timestamp))
        self.market_state.order_book.bids.sort(key=lambda o: (-o.price, o.timestamp))

        matched: list[Trade] = []
        bids = self.market_state.order_book.bids
        asks = self.market_state.order_book.asks

        while bids and asks:
            best_bid = bids[0]
            best_ask = asks[0]

            if best_bid.price < best_ask.price:
                break

            trade_qty = min(best_bid.quantity, best_ask.quantity)

            if clearing_mechanism == "call_auction":
                clearing_price = (best_bid.price + best_ask.price) / 2.0
            else:
                clearing_price = best_ask.price if clearing_mechanism == "continuous" else (best_bid.price + best_ask.price) / 2.0

            trade = Trade(
                trade_id=f"trade-{time.time()}",
                buyer_id=best_bid.agent_id,
                seller_id=best_ask.agent_id,
                price=clearing_price,
                quantity=trade_qty,
                timestamp=time.time(),
            )
            matched.append(trade)

            self.market_state.order_book.last_clearing_price = clearing_price
            self._update_price_history(clearing_price)

            buyer_portfolio = self._get_portfolio(best_bid.agent_id)
            seller_portfolio = self._get_portfolio(best_ask.agent_id)

            buyer_portfolio.cash -= clearing_price * trade_qty
            buyer_portfolio.adjust_balance(best_bid.metadata.get("resource", "default"), trade_qty)
            seller_portfolio.cash += clearing_price * trade_qty
            seller_portfolio.adjust_balance(best_ask.metadata.get("resource", "default"), -trade_qty)

            buyer_portfolio.record_trade({
                "trade_id": trade.trade_id,
                "type": "buy",
                "price": clearing_price,
                "quantity": trade_qty,
                "timestamp": trade.timestamp,
            })
            seller_portfolio.record_trade({
                "trade_id": trade.trade_id,
                "type": "sell",
                "price": clearing_price,
                "quantity": trade_qty,
                "timestamp": trade.timestamp,
            })

            best_bid.quantity -= trade_qty
            best_ask.quantity -= trade_qty

            if best_bid.quantity <= 0:
                bids.pop(0)
            if best_ask.quantity <= 0:
                asks.pop(0)

        self.market_state.order_book.bids = bids
        self.market_state.order_book.asks = asks
        self._update_market_depth()

        for t in matched:
            t.status = TradeStatus.CONFIRMED

        return matched

    def invest(self, agent_id: str, amount: float, resource: str = "infrastructure") -> dict[str, Any]:
        if agent_id not in self.world_state.agents:
            return {"status": TradeStatus.REJECTED, "reason": "agent_not_found"}

        portfolio = self._get_portfolio(agent_id)
        yield_rate = self.market_state.yields.get(resource, 0.0)
        liquidity = self.market_state.liquidity.get(resource, 0.0)
        if yield_rate <= 0 or liquidity <= 0:
            return {"status": TradeStatus.REJECTED, "reason": "invalid_market_conditions"}

        portfolio.cash -= amount
        portfolio.infrastructure_level += amount * liquidity

        investment = {
            "agent_id": agent_id,
            "amount": amount,
            "resource": resource,
            "yield_rate": yield_rate,
            "liquidity": liquidity,
            "timestamp": time.time(),
        }
        portfolio.trade_history.append(investment)
        return {"status": "confirmed", "investment": investment}

    def auction_bid(self, agent_id: str, bid_price: float, resource: str = "auction_resource") -> dict[str, Any]:
        if agent_id not in self.world_state.agents:
            return {"status": TradeStatus.REJECTED, "reason": "agent_not_found"}

        portfolio = self._get_portfolio(agent_id)
        if self.market_state.order_book.asks:
            min_ask = min(self.market_state.order_book.asks, key=lambda o: o.price)
            if bid_price < min_ask.price:
                return {"status": TradeStatus.REJECTED, "reason": "price_below_minimum", "minimum_price": min_ask.price}

        base_liquidity = self.market_state.liquidity.get(resource, 0.5)
        quantity = portfolio.cash * base_liquidity / bid_price if bid_price > 0 else 0.0

        return {
            "status": "accepted",
            "bid_accepted": True,
            "bid_price": bid_price,
            "quantity": quantity,
            "resource": resource,
        }

    def get_market_snapshot(self) -> dict[str, Any]:
        bids = self.market_state.order_book.bids
        asks = self.market_state.order_book.asks

        depth = {}
        for order in bids:
            p = order.price
            depth.setdefault(p, {"bids": 0.0, "asks": 0.0})
            depth[p]["bids"] += order.quantity
        for order in asks:
            p = order.price
            depth.setdefault(p, {"bids": 0.0, "asks": 0.0})
            depth[p]["asks"] += order.quantity

        mid = self.market_state.order_book.last_clearing_price
        if not mid and not asks and not bids:
            mid = 0.0

        return {
            "current_price": mid,
            "order_book_depth": depth,
            "yields": self.market_state.yields,
            "liquidity": self.market_state.liquidity,
            "price_history": self.market_state.price_history[-20:],
        }

    def get_portfolio(self, agent_id: str) -> dict[str, Any] | None:
        if agent_id not in self.agent_portfolios:
            return None
        return self.agent_portfolios[agent_id].model_dump()

    def _get_portfolio(self, agent_id: str) -> Portfolio:
        if agent_id not in self.agent_portfolios:
            portfolio = Portfolio(agent_id=agent_id)
            portfolio.resources["default"] = 20.0
            self.agent_portfolios[agent_id] = portfolio
        return self.agent_portfolios[agent_id]

    def _update_price_history(self, price: float) -> None:
        self.market_state.price_history.append(price)
        self.market_state.current_price = price
        self.market_state.last_update = time.time()

    def _update_market_depth(self) -> None:
        bid_depth = sum(o.quantity for o in self.market_state.order_book.bids)
        ask_depth = sum(o.quantity for o in self.market_state.order_book.asks)
        self.market_state.order_book.market_depth = min(bid_depth, ask_depth)
