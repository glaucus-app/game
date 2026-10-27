import pytest
from src.encounters.economy import EconomyEngine
from src.models.world import WorldState, AgentState


@pytest.fixture
def engine():
    ws = WorldState()
    ws.agents["agent1"] = AgentState(agent_id="agent1")
    ws.agents["agent2"] = AgentState(agent_id="agent2")
    ws.agents["agent3"] = AgentState(agent_id="agent3")
    return EconomyEngine(ws)


class TestPlaceBid:
    def test_place_bid_success(self, engine):
        result = engine.place_bid("agent1", price=10.0, quantity=5.0)
        assert result["status"] == "accepted"
        assert result["side"] == "bid"
        assert result["price"] == 10.0
        assert result["quantity"] == 5.0
        assert len(engine.market_state.order_book.bids) == 1

    def test_place_bid_rejects_unknown_agent(self, engine):
        result = engine.place_bid("ghost", price=10.0, quantity=5.0)
        assert result["status"] == "rejected"
        assert result["reason"] == "agent_not_found"

    def test_place_bid_rejects_insufficient_cash(self, engine):
        result = engine.place_bid("agent1", price=100000.0, quantity=10000.0)
        assert result["status"] == "rejected"
        assert result["reason"] == "insufficient_margin"


class TestPlaceAsk:
    def test_place_ask_success(self, engine):
        result = engine.place_ask("agent1", price=12.0, quantity=5.0)
        assert result["status"] == "accepted"
        assert result["side"] == "ask"
        assert len(engine.market_state.order_book.asks) == 1

    def test_place_ask_rejects_unknown_agent(self, engine):
        result = engine.place_ask("ghost", price=12.0, quantity=5.0)
        assert result["status"] == "rejected"
        assert result["reason"] == "agent_not_found"

    def test_place_ask_rejects_insufficient_resource(self, engine):
        result = engine.place_ask("agent1", price=12.0, quantity=1.0, resource="gold")
        assert result["status"] == "rejected"
        assert result["reason"] == "insufficient_resource"


class TestOrderMatching:
    def test_no_match_when_bid_below_ask(self, engine):
        engine.place_bid("agent1", price=8.0, quantity=5.0)
        engine.place_ask("agent2", price=10.0, quantity=5.0)
        trades = engine.match_orders()
        assert trades == []

    def test_single_order_matched(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=3.0)
        engine.place_ask("agent2", price=9.0, quantity=3.0)
        trades = engine.match_orders()
        assert len(trades) == 1
        assert trades[0].status == "confirmed"
        assert trades[0].quantity == 3.0

    def test_partial_fill(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=10.0)
        engine.place_ask("agent2", price=9.0, quantity=4.0)
        trades = engine.match_orders()
        assert len(trades) == 1
        assert trades[0].quantity == 4.0
        leftover_bids = engine.market_state.order_book.bids
        assert len(leftover_bids) == 1
        assert leftover_bids[0].quantity == 6.0

    def test_multiple_orders_matched(self, engine):
        engine.place_bid("agent1", price=11.0, quantity=3.0)
        engine.place_bid("agent3", price=10.0, quantity=5.0)
        engine.place_ask("agent2", price=9.0, quantity=7.0)
        trades = engine.match_orders()
        assert len(trades) == 2
        total_qty = sum(t.quantity for t in trades)
        assert total_qty == 7.0

    def test_call_auction_clearing_price(self, engine):
        engine.place_bid("agent1", price=12.0, quantity=5.0)
        engine.place_ask("agent2", price=10.0, quantity=5.0)
        trades = engine.match_orders(clearing_mechanism="call_auction")
        assert len(trades) == 1
        assert trades[0].price == 11.0

    def test_continuous_clearing_uses_ask_price(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=5.0)
        engine.place_ask("agent2", price=8.0, quantity=5.0)
        trades = engine.match_orders(clearing_mechanism="continuous")
        assert trades[0].price == 8.0

    def test_matched_portfolio_updates(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=2.0)
        engine.place_ask("agent2", price=9.0, quantity=2.0)
        engine.match_orders()
        p1 = engine.get_portfolio("agent1")
        p2 = engine.get_portfolio("agent2")
        assert p1["resources"].get("default", 0.0) == 22.0
        assert p1["cash"] == 10000.0 - 18.0
        assert p2["resources"].get("default", 0.0) == 18.0
        assert p2["cash"] == 10000.0 + 18.0
        assert len(p1["trade_history"]) == 1
        assert len(p2["trade_history"]) == 1


class TestInvest:
    def test_invest_success(self, engine):
        engine.market_state.yields["infra"] = 0.1
        engine.market_state.liquidity["infra"] = 0.5
        result = engine.invest("agent1", 1000.0, "infra")
        assert result["status"] == "confirmed"
        portfolio = engine.agent_portfolios["agent1"]
        assert portfolio.cash == 9000.0
        assert portfolio.infrastructure_level == 500.0

    def test_invest_rejects_unknown_agent(self, engine):
        result = engine.invest("ghost", 1000.0)
        assert result["status"] == "rejected"
        assert result["reason"] == "agent_not_found"

    def test_invest_rejects_invalid_market(self, engine):
        result = engine.invest("agent1", 1000.0, "bad_resource")
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_market_conditions"


class TestAuctionBid:
    def test_auction_bid_accepts(self, engine):
        engine.market_state.current_price = 5.0
        result = engine.auction_bid("agent1", 10.0)
        assert result["bid_accepted"] is True
        assert result["status"] == "accepted"

    def test_auction_bid_rejects_unknown_agent(self, engine):
        result = engine.auction_bid("ghost", 10.0)
        assert result["status"] == "rejected"
        assert result["reason"] == "agent_not_found"

    def test_auction_bid_rejects_below_min_ask(self, engine):
        engine.market_state.current_price = 10.0
        engine.place_ask("agent2", price=15.0, quantity=5.0)
        result = engine.auction_bid("agent1", 12.0)
        assert result["status"] == "rejected"
        assert result["reason"] == "price_below_minimum"


class TestMarketSnapshot:
    def test_snapshot_returns_correct_structure(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=3.0)
        engine.place_ask("agent2", price=12.0, quantity=4.0)
        snapshot = engine.get_market_snapshot()
        assert "current_price" in snapshot
        assert "order_book_depth" in snapshot
        assert "yields" in snapshot
        assert "liquidity" in snapshot
        assert "price_history" in snapshot

    def test_snapshot_price_history_truncated(self, engine):
        for i in range(30):
            engine.market_state.current_price = float(i)
            engine._update_price_history(float(i))
        snapshot = engine.get_market_snapshot()
        assert len(snapshot["price_history"]) == 20


class TestPriceDiscovery:
    def test_clearing_price_updates_current_price(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=5.0)
        engine.place_ask("agent2", price=9.0, quantity=5.0)
        engine.match_orders()
        assert engine.market_state.current_price == 9.0

    def test_last_clearing_price_recorded(self, engine):
        engine.place_bid("agent1", price=10.0, quantity=3.0)
        engine.place_ask("agent2", price=8.0, quantity=3.0)
        engine.match_orders()
        assert engine.market_state.order_book.last_clearing_price == 8.0


class TestPortfolioTracking:
    def test_initial_portfolio_cash(self, engine):
        engine._get_portfolio("agent1")
        p = engine.get_portfolio("agent1")
        assert p["cash"] == 10000.0

    def test_get_portfolio_returns_none_for_unknown(self, engine):
        assert engine.get_portfolio("ghost") is None

    def test_initial_portfolio_seeded_resource(self, engine):
        engine._get_portfolio("agent1")
        p = engine.get_portfolio("agent1")
        assert p["resources"]["default"] == 20.0
