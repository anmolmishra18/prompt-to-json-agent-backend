#!/usr/bin/env python3
"""Validation script to ensure all components work"""

def test_imports():
    """Test all imports work correctly"""
    try:
        from app.main import app
        from app.services.prompt_agent import PromptAgent
        from app.services.evaluator import Evaluator
        from app.services.rl_agent import RLAgent
        from app.services.feedback import FeedbackEngine
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_services():
    """Test all services work correctly"""
    try:
        from app.services.prompt_agent import PromptAgent
        from app.services.evaluator import Evaluator
        from app.services.rl_agent import RLAgent
        
        # Test PromptAgent
        agent = PromptAgent()
        spec = agent.run("design a robot using aluminium; Priority: high")
        assert "title" in spec and "description" in spec and "priority" in spec
        print("✓ PromptAgent working")
        
        # Test Evaluator
        evaluator = Evaluator()
        result = evaluator.run(spec)
        assert "score" in result and "comments" in result
        print("✓ Evaluator working")
        
        # Test RLAgent
        rl = RLAgent()
        history = rl.run("design a robot", max_iters=1)
        assert len(history) == 1
        assert "iteration_number" in history[0]
        print("✓ RLAgent working")
        
        return True
    except Exception as e:
        print(f"✗ Service error: {e}")
        return False

def test_database():
    """Test database models work"""
    try:
        from app.database import Base, engine
        from app import models
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

if __name__ == "__main__":
    print("Validating Prompt-to-JSON Agent Backend...")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_services()
    success &= test_database()
    
    print("=" * 40)
    if success:
        print("All validations passed! Project is ready.")
        print("\nTo start the server:")
        print("  python run.py")
        print("  OR")
        print("  python -m uvicorn app.main:app --reload")
        print("\nThen visit: http://127.0.0.1:8000/docs")
    else:
        print("Some validations failed. Check errors above.")