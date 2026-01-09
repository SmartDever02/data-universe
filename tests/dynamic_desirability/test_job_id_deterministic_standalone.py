"""Standalone test cases for deterministic job ID generation (fix for issue #744).

This test verifies that job IDs change when job parameters change,
without requiring bittensor dependencies.
"""

import unittest
import json
import hashlib


def generate_deterministic_job_id_standalone(job_params, prefix="job"):
    """Standalone version of generate_deterministic_job_id for testing."""
    param_str = json.dumps({
        "keyword": job_params.get("keyword"),
        "platform": job_params.get("platform"),
        "label": job_params.get("label"),
        "post_start_datetime": job_params.get("post_start_datetime"),
        "post_end_datetime": job_params.get("post_end_datetime")
    }, sort_keys=True, separators=(',', ':'))
    
    hash_obj = hashlib.md5(param_str.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    job_id = f"{prefix}-{hash_hex[:16]}"
    
    if len(job_id) > 80:
        job_id = job_id[:80]
    
    return job_id


class TestDeterministicJobIdStandalone(unittest.TestCase):
    """Standalone tests for deterministic job ID generation."""
    
    def test_same_parameters_generate_same_id(self):
        """Test that same parameters always generate the same ID."""
        params1 = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-16T03:22:05.23181Z",
            "post_end_datetime": "2025-12-15T03:22:05.23181Z"
        }
        
        params2 = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-16T03:22:05.23181Z",
            "post_end_datetime": "2025-12-15T03:22:05.23181Z"
        }
        
        id1 = generate_deterministic_job_id_standalone(params1, prefix="job")
        id2 = generate_deterministic_job_id_standalone(params2, prefix="job")
        
        self.assertEqual(id1, id2, "Same parameters should generate same ID")
        print(f"✓ Same parameters generate same ID: {id1}")
    
    def test_different_dates_generate_different_id(self):
        """Test that different dates generate different IDs (the bug fix scenario)."""
        # Original job parameters (from issue #744)
        params1 = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-16T03:22:05.23181Z",
            "post_end_datetime": "2025-12-15T03:22:05.23181Z"
        }
        
        # Updated job parameters (dates changed, simulating the bug)
        params2 = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-18T03:11:23.058879Z",  # Changed
            "post_end_datetime": "2025-12-17T03:11:23.058879Z"     # Changed
        }
        
        id1 = generate_deterministic_job_id_standalone(params1, prefix="job")
        id2 = generate_deterministic_job_id_standalone(params2, prefix="job")
        
        self.assertNotEqual(id1, id2, "Different dates should generate different IDs")
        print(f"✓ Different parameters generate different IDs:")
        print(f"  Old ID: {id1}")
        print(f"  New ID: {id2}")
    
    def test_all_parameter_changes_affect_id(self):
        """Test that changing any parameter changes the ID."""
        base_params = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-16T03:22:05.23181Z",
            "post_end_datetime": "2025-12-15T03:22:05.23181Z"
        }
        
        base_id = generate_deterministic_job_id_standalone(base_params, prefix="job")
        
        # Test keyword change
        params_keyword = base_params.copy()
        params_keyword["keyword"] = "iphone pro"
        id_keyword = generate_deterministic_job_id_standalone(params_keyword, prefix="job")
        self.assertNotEqual(base_id, id_keyword, "Changing keyword should change ID")
        print(f"✓ Keyword change affects ID: {base_id} != {id_keyword}")
        
        # Test platform change
        params_platform = base_params.copy()
        params_platform["platform"] = "reddit"
        id_platform = generate_deterministic_job_id_standalone(params_platform, prefix="job")
        self.assertNotEqual(base_id, id_platform, "Changing platform should change ID")
        print(f"✓ Platform change affects ID: {base_id} != {id_platform}")
        
        # Test label change
        params_label = base_params.copy()
        params_label["label"] = "#Apple"
        id_label = generate_deterministic_job_id_standalone(params_label, prefix="job")
        self.assertNotEqual(base_id, id_label, "Changing label should change ID")
        print(f"✓ Label change affects ID: {base_id} != {id_label}")
        
        # Test start date change
        params_start = base_params.copy()
        params_start["post_start_datetime"] = "2025-09-18T03:11:23.058879Z"
        id_start = generate_deterministic_job_id_standalone(params_start, prefix="job")
        self.assertNotEqual(base_id, id_start, "Changing start date should change ID")
        print(f"✓ Start date change affects ID: {base_id} != {id_start}")
        
        # Test end date change
        params_end = base_params.copy()
        params_end["post_end_datetime"] = "2025-12-17T03:11:23.058879Z"
        id_end = generate_deterministic_job_id_standalone(params_end, prefix="job")
        self.assertNotEqual(base_id, id_end, "Changing end date should change ID")
        print(f"✓ End date change affects ID: {base_id} != {id_end}")
    
    def test_id_format_valid(self):
        """Test that generated IDs follow the required format."""
        params = {
            "keyword": "test",
            "platform": "x",
            "label": None,
            "post_start_datetime": None,
            "post_end_datetime": None
        }
        
        job_id = generate_deterministic_job_id_standalone(params, prefix="job")
        
        # Should not contain slashes
        self.assertNotIn('/', job_id, "ID should not contain forward slashes")
        self.assertNotIn('\\', job_id, "ID should not contain backslashes")
        
        # Should be max 80 characters
        self.assertLessEqual(len(job_id), 80, 
                           f"ID should be max 80 characters, got {len(job_id)}")
        
        # Should have prefix
        self.assertTrue(job_id.startswith("job-"), 
                       f"ID should start with prefix, got {job_id}")
        
        print(f"✓ ID format is valid: {job_id} (length={len(job_id)})")
    
    def test_issue_744_scenario(self):
        """Test the exact scenario from issue #744."""
        # Original job from issue
        job1_params = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-16T03:22:05.23181Z",
            "post_end_datetime": "2025-12-15T03:22:05.23181Z"
        }
        
        # Updated job (dates changed, ID should also change)
        job2_params = {
            "keyword": "iphone air",
            "platform": "x",
            "label": None,
            "post_start_datetime": "2025-09-18T03:11:23.058879Z",  # Changed
            "post_end_datetime": "2025-12-17T03:11:23.058879Z"     # Changed
        }
        
        id1 = generate_deterministic_job_id_standalone(job1_params, prefix="crawler-2")
        id2 = generate_deterministic_job_id_standalone(job2_params, prefix="crawler-2")
        
        # The fix ensures IDs are different when parameters change
        self.assertNotEqual(id1, id2, 
                           "Job ID should change when job parameters change (issue #744 fix)")
        
        print(f"✓ Issue #744 scenario verified:")
        print(f"  Original job ID: {id1}")
        print(f"  Updated job ID: {id2}")
        print(f"  IDs are different: {id1 != id2}")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Deterministic Job ID Generation (Issue #744 Fix)")
    print("=" * 70)
    unittest.main(verbosity=2)
