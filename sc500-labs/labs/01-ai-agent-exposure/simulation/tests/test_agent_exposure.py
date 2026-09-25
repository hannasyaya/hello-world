import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_exposure import DEFAULT_MODEL, Environment  # noqa: E402


class AgentExposureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = Environment.load(DEFAULT_MODEL)

    def test_all_edges_reference_known_nodes(self):
        for e in self.env.data["edges"]:
            self.assertIn(e["from"], self.env.nodes, e)
            self.assertIn(e["to"], self.env.nodes, e)

    def test_inventory_flags_anonymous_and_orphaned_agents(self):
        rows = {r["id"]: r["findings"] for r in self.env.inventory()}
        self.assertIn("No user authentication", rows["agent-hr-benefits"])
        self.assertIn("Orphaned (all owners disabled)", rows["agent-marketing"])
        self.assertTrue(any("Contributor" in f for f in rows["agent-devops"]))

    def test_devops_blast_radius_crosses_into_finance_blueprint(self):
        reached = self.env.blast_radius("agent-devops")
        self.assertIn("bp-finance", reached)
        self.assertIn("all-mailboxes", reached)
        self.assertEqual(reached["all-mailboxes"][0], 6)

    def test_blueprint_controls_all_child_identities(self):
        self.assertEqual(self.env.blueprint_of("ai-invoice-01"), "bp-finance")
        self.assertCountEqual(self.env.siblings("bp-finance"),
                              ["ai-invoice-01", "ai-invoice-02", "ai-expense-01"])

    def test_marketing_agent_has_no_path_to_critical_assets(self):
        paths = self.env.attack_paths()
        self.assertFalse(any("agent-marketing" in p for p, _ in paths))
        self.assertTrue(all(self.env.is_critical(p[-1]) for p, _ in paths))

    def test_devops_identity_is_top_choke_point(self):
        top = dict(self.env.choke_points(self.env.attack_paths()))
        self.assertEqual(top["mi-agent-devops"], max(top.values()))


if __name__ == "__main__":
    unittest.main()
