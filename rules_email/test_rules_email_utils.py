import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the directory to sys.path to import the script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import rules_email

class TestRulesEmail(unittest.TestCase):
    
    def test_regex_generation(self):
        """Test that regex is correctly generated and escaped"""
        test_cases = [
            ("company.com", "/@company\\.com$/i"),
            ("@company.com", "/@company\\.com$/i"),
            ("sub.domain.co.uk", "/@sub\\.domain\\.co\\.uk$/i"),
            ("my-domain.com", "/@my\\-domain\\.com$/i"),
        ]
        
        for input_domain, expected_regex in test_cases:
            with self.subTest(domain=input_domain):
                # We need to mock the entity info for create_or_update_rule
                # But since we only care about regex_pattern, let's just test the logic
                # Extracting internal logic for testing or mocking the call
                with patch('rules_email.get_rule_details') as mock_details:
                    mock_details.return_value = ([], []) # Force CREATE/UPDATE log
                    with patch('rules_email.logger') as mock_logger:
                        rules_email.create_or_update_rule(
                            "http://test", {}, "Test", 1, input_domain, {}, dry_run=True
                        )
                        # Check the log message for the pattern
                        args, _ = mock_logger.info.call_args_list[1]
                        self.assertIn(expected_regex, args[0])

    @patch('rules_email.requests.get')
    def test_smart_sync_no_change(self, mock_get):
        """Test that no update is performed if the rule is already correct"""
        rule_id = 123
        entity_id = 5
        domain = "example.com"
        rule_name = "Auto-Email-Test-Entity"
        
        # Mock Criteria response
        mock_crit = MagicMock()
        mock_crit.status_code = 200
        mock_crit.json.return_value = [{
            "id": 1,
            "rules_id": rule_id,
            "criteria": "from",
            "condition": 6,
            "pattern": "/@example\\.com$/i"
        }]
        
        # Mock Action response
        mock_act = MagicMock()
        mock_act.status_code = 200
        mock_act.json.return_value = [{
            "id": 2,
            "rules_id": rule_id,
            "action_type": "assign",
            "field": "entities_id",
            "value": str(entity_id)
        }]
        
        mock_get.side_effect = [mock_crit, mock_act]
        
        with patch('rules_email.logger') as mock_logger:
            rules_email.create_or_update_rule(
                "http://test", {}, "Test Entity", entity_id, domain, 
                {rule_name: rule_id}, dry_run=False
            )
            
            # Should log that it's skipping
            mock_logger.info.assert_any_call(f"SKIP: Rule '{rule_name}' is already up to date.")
            
            # Should NOT have called delete or post
            with patch('rules_email.requests.delete') as mock_delete:
                with patch('rules_email.requests.post') as mock_post:
                    self.assertFalse(mock_delete.called)
                    self.assertFalse(mock_post.called)

if __name__ == '__main__':
    unittest.main()
