#!/usr/bin/env python
import sys
import os
import json
import warnings
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import PyPDF2
import io

from test_gemini.crew import TestGemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# -------------------------------
# 📄 PDF Processing Function
# -------------------------------
def extract_text_from_pdf(pdf_file):
    """
    Extract text content from uploaded PDF file.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        if not text_content.strip():
            raise Exception("No text content found in PDF")
            
        return text_content.strip()
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

# -------------------------------
# 🧠 Individual Agent Functions
# -------------------------------
def run_requirements_analyst(topic: str, current_year: str = None):
    """
    Run only the Requirements Analyst agent.
    """
    try:
        inputs = {
            'topic': topic,
            'current_year': current_year or str(datetime.now().year)
        }
        
        logger.info(f"Starting Requirements Analysis for topic: {topic}")
        
        # Get the crew instance
        crew_instance = TestGemini()
        
        # Execute only the requirements analyst task
        # You'll need to modify this based on your actual crew structure
        # This assumes you can access individual agents/tasks
        requirements_result = crew_instance.crew().agents[0].execute_task(
            crew_instance.crew().tasks[0], 
            inputs
        )
        
        logger.info(f"Requirements Analysis completed for topic: {topic}")
        return True, f"Requirements analysis completed for topic: {topic}", str(requirements_result)

    except Exception as e:
        logger.error(f"Requirements analysis failed for topic {topic}: {str(e)}")
        return False, f"Error in requirements analysis: {str(e)}", None

def run_test_case_designer(topic: str, current_year: str = None):
    """
    Run only the Test Case Designer agent.
    """
    try:
        inputs = {
            'topic': topic,
            'current_year': current_year or str(datetime.now().year)
        }
        
        logger.info(f"Starting Test Case Design for topic: {topic}")
        
        # Get the crew instance
        crew_instance = TestGemini()
        
        # Execute only the test case designer task
        test_design_result = crew_instance.crew().agents[1].execute_task(
            crew_instance.crew().tasks[1], 
            inputs
        )
        
        logger.info(f"Test Case Design completed for topic: {topic}")
        return True, f"Test case design completed for topic: {topic}", str(test_design_result)

    except Exception as e:
        logger.error(f"Test case design failed for topic {topic}: {str(e)}")
        return False, f"Error in test case design: {str(e)}", None

def run_test_implementer(topic: str, current_year: str = None):
    """
    Run only the Test Implementation agent.
    """
    try:
        inputs = {
            'topic': topic,
            'current_year': current_year or str(datetime.now().year)
        }
        
        logger.info(f"Starting Test Implementation for topic: {topic}")
        
        # Get the crew instance
        crew_instance = TestGemini()
        
        # Execute only the test implementer task
        implementation_result = crew_instance.crew().agents[2].execute_task(
            crew_instance.crew().tasks[2], 
            inputs
        )
        
        logger.info(f"Test Implementation completed for topic: {topic}")
        return True, f"Test implementation completed for topic: {topic}", str(implementation_result)

    except Exception as e:
        logger.error(f"Test implementation failed for topic {topic}: {str(e)}")
        return False, f"Error in test implementation: {str(e)}", None

# -------------------------------
# 🧠 Core CrewAI pipeline logic (existing)
# -------------------------------
def run_crew_pipeline(topic: str, current_year: str = None):
    """
    Run the crew for requirements analysis, test case design, and test script implementation.
    """
    try:
        inputs = {
            'topic': topic,
            'current_year': current_year or str(datetime.now().year)
        }
        
        logger.info(f"Starting CrewAI pipeline for topic: {topic}")
        
        # Run CrewAI pipeline
        crew_result = TestGemini().crew().kickoff(inputs=inputs)
        
        # Process crew result
        if hasattr(crew_result, 'text'):
            crew_result_text = crew_result.text
        elif hasattr(crew_result, 'dict'):
            crew_result_text = json.dumps(crew_result.dict())
        elif isinstance(crew_result, (list, dict)):
            crew_result_text = json.dumps(crew_result)
        elif crew_result is None:
            return False, "crew_result is None"
        else:
            crew_result_text = str(crew_result)
        
        logger.info(f"CrewAI pipeline completed successfully for topic: {topic}")
        return True, f"Success: Requirements analysis, test case design, and test script implementation completed for topic: {topic}", crew_result_text

    except Exception as e:
        logger.error(f"Pipeline failed for topic {topic}: {str(e)}")
        return False, f"Error: {str(e)}", None

# -------------------------------
# 🚀 Flask App inside run()
# -------------------------------
def run():
    app = Flask(__name__)
    app.secret_key = 'crew_ai_secret_key'
    
    # Enable CORS for localhost:3000
    CORS(app, origins=['http://localhost:3000'])

    @app.route('/')
    def index():
        return jsonify({
            "message": "CrewAI Requirements & Testing API is running",
            "usage": {
                "full_pipeline": {
                    "run_crew": "POST /run with {'topic': 'Your Topic'}",
                    "run_crew_pdf": "POST /run/pdf with PDF file upload"
                },
                "individual_agents": {
                    "requirements": "POST /requirements with {'topic': 'Your Topic'} or GET /requirements/<topic>",
                    "requirements_pdf": "POST /requirements/pdf with PDF file upload",
                    "test_design": "POST /test-design with {'topic': 'Your Topic'} or GET /test-design/<topic>",
                    "test_design_pdf": "POST /test-design/pdf with PDF file upload",
                    "test_implementation": "POST /test-implementation with {'topic': 'Your Topic'} or GET /test-implementation/<topic>",
                    "test_implementation_pdf": "POST /test-implementation/pdf with PDF file upload"
                },
                "training": {
                    "train": "POST /train with training parameters",
                    "test": "POST /test with testing parameters",
                    "replay": "POST /replay with {'task_id': 'task_id'}"
                }
            },
            "health_check": "/health",
            "version": "2.1.0"
        })

    # -------------------------------
    # 🎯 Individual Agent Endpoints
    # -------------------------------
    
    @app.route('/requirements', methods=['POST'])
    def requirements_analysis_post():
        """POST endpoint for Requirements Analysis only"""
        try:
            data = request.get_json()
            if not data or 'topic' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Topic is required in request body"
                }), 400
            
            topic = data['topic']
            current_year = data.get('current_year')
            
            logger.info(f"Processing requirements analysis for topic: {topic}")
            success, message, result = run_requirements_analyst(topic, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "agent": "Requirements Analyst",
                "topic": topic,
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in requirements endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/requirements/pdf', methods=['POST'])
    def requirements_analysis_pdf():
        """POST endpoint for Requirements Analysis with PDF upload"""
        try:
            if 'pdf_file' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "PDF file is required"
                }), 400
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "No file selected"
                }), 400
            
            if not pdf_file.filename.lower().endswith('.pdf'):
                return jsonify({
                    "status": "error",
                    "message": "Only PDF files are allowed"
                }), 400
            
            # Extract text from PDF
            pdf_content = extract_text_from_pdf(pdf_file)
            current_year = request.form.get('current_year')
            
            logger.info(f"Processing requirements analysis for PDF: {pdf_file.filename}")
            success, message, result = run_requirements_analyst(pdf_content, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "agent": "Requirements Analyst",
                "source": f"PDF: {pdf_file.filename}",
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in requirements PDF endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/requirements/<topic>', methods=['GET'])
    def requirements_analysis_get(topic):
        """GET endpoint for Requirements Analysis with topic in URL"""
        if not topic:
            return jsonify({
                "status": "error",
                "message": "Topic is required"
            }), 400
        
        logger.info(f"Processing requirements analysis for topic: {topic}")
        success, message, result = run_requirements_analyst(topic)
        
        response_data = {
            "status": "success" if success else "error",
            "agent": "Requirements Analyst",
            "topic": topic,
            "message": message
        }
        
        if success and result:
            response_data["result"] = result
        
        return jsonify(response_data), 200 if success else 500

    @app.route('/test-design', methods=['POST'])
    def test_design_post():
        """POST endpoint for Test Case Design only"""
        try:
            data = request.get_json()
            if not data or 'topic' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Topic is required in request body"
                }), 400
            
            topic = data['topic']
            current_year = data.get('current_year')
            
            logger.info(f"Processing test case design for topic: {topic}")
            success, message, result = run_test_case_designer(topic, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "agent": "Test Case Designer",
                "topic": topic,
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in test design endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/test-design/pdf', methods=['POST'])
    def test_design_pdf():
        """POST endpoint for Test Case Design with PDF upload"""
        try:
            if 'pdf_file' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "PDF file is required"
                }), 400
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "No file selected"
                }), 400
            
            if not pdf_file.filename.lower().endswith('.pdf'):
                return jsonify({
                    "status": "error",
                    "message": "Only PDF files are allowed"
                }), 400
            
            # Extract text from PDF
            pdf_content = extract_text_from_pdf(pdf_file)
            current_year = request.form.get('current_year')
            
            logger.info(f"Processing test case design for PDF: {pdf_file.filename}")
            success, message, result = run_test_case_designer(pdf_content, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "agent": "Test Case Designer",
                "source": f"PDF: {pdf_file.filename}",
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in test design PDF endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/test-design/<topic>', methods=['GET'])
    def test_design_get(topic):
        """GET endpoint for Test Case Design with topic in URL"""
        if not topic:
            return jsonify({
                "status": "error",
                "message": "Topic is required"
            }), 400
        
        logger.info(f"Processing test case design for topic: {topic}")
        success, message, result = run_test_case_designer(topic)
        
        response_data = {
            "status": "success" if success else "error",
            "agent": "Test Case Designer",
            "topic": topic,
            "message": message
        }
        
        if success and result:
            response_data["result"] = result
        
        return jsonify(response_data), 200 if success else 500

    @app.route('/test-implementation', methods=['POST'])
    def test_implementation_post():
        """POST endpoint for Test Implementation only"""
        try:
            data = request.get_json()
            if not data or 'topic' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Topic is required in request body"
                }), 400
            
            topic = data['topic']
            current_year = data.get('current_year')
            
            logger.info(f"Processing test implementation for topic: {topic}")
            success, message, result = run_test_implementer(topic, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "agent": "Test Implementer",
                "topic": topic,
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in test implementation endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/test-implementation/pdf', methods=['POST'])
    def test_implementation_pdf():
        """POST endpoint for Test Implementation with PDF upload"""
        try:
            if 'pdf_file' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "PDF file is required"
                }), 400
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "No file selected"
                }), 400
            
            if not pdf_file.filename.lower().endswith('.pdf'):
                return jsonify({
                    "status": "error",
                    "message": "Only PDF files are allowed"
                }), 400
            
            # Extract text from PDF
            pdf_content = extract_text_from_pdf(pdf_file)
            current_year = request.form.get('current_year')
            
            logger.info(f"Processing test implementation for PDF: {pdf_file.filename}")
            success, message, result = run_test_implementer(pdf_content, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "agent": "Test Implementer",
                "source": f"PDF: {pdf_file.filename}",
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in test implementation PDF endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/test-implementation/<topic>', methods=['GET'])
    def test_implementation_get(topic):
        """GET endpoint for Test Implementation with topic in URL"""
        if not topic:
            return jsonify({
                "status": "error",
                "message": "Topic is required"
            }), 400
        
        logger.info(f"Processing test implementation for topic: {topic}")
        success, message, result = run_test_implementer(topic)
        
        response_data = {
            "status": "success" if success else "error",
            "agent": "Test Implementer",
            "topic": topic,
            "message": message
        }
        
        if success and result:
            response_data["result"] = result
        
        return jsonify(response_data), 200 if success else 500

    # -------------------------------
    # 🔄 Full Pipeline Endpoints
    # -------------------------------

    @app.route('/run', methods=['POST'])
    def run_pipeline_route():
        """POST endpoint to run crew pipeline with topic"""
        try:
            data = request.get_json()
            if not data or 'topic' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Topic is required in request body"
                }), 400
            
            topic = data['topic']
            current_year = data.get('current_year')
            
            logger.info(f"Processing crew pipeline for topic: {topic}")
            success, message, result = run_crew_pipeline(topic, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "pipeline": "Full CrewAI Pipeline",
                "topic": topic,
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in run endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/run/pdf', methods=['POST'])
    def run_pipeline_pdf():
        """POST endpoint to run crew pipeline with PDF upload"""
        try:
            if 'pdf_file' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "PDF file is required"
                }), 400
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "No file selected"
                }), 400
            
            if not pdf_file.filename.lower().endswith('.pdf'):
                return jsonify({
                    "status": "error",
                    "message": "Only PDF files are allowed"
                }), 400
            
            # Extract text from PDF
            pdf_content = extract_text_from_pdf(pdf_file)
            current_year = request.form.get('current_year')
            
            logger.info(f"Processing crew pipeline for PDF: {pdf_file.filename}")
            success, message, result = run_crew_pipeline(pdf_content, current_year)
            
            response_data = {
                "status": "success" if success else "error",
                "pipeline": "Full CrewAI Pipeline",
                "source": f"PDF: {pdf_file.filename}",
                "message": message
            }
            
            if success and result:
                response_data["result"] = result
            
            return jsonify(response_data), 200 if success else 500
            
        except Exception as e:
            logger.error(f"Error in run PDF endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500

    @app.route('/run/<topic>', methods=['GET'])
    def run_pipeline_get_route(topic):
        """GET endpoint to run crew pipeline with topic in URL"""
        if not topic:
            return jsonify({
                "status": "error",
                "message": "Topic is required"
            }), 400
        
        logger.info(f"Processing crew pipeline for topic: {topic}")
        success, message, result = run_crew_pipeline(topic)
        
        response_data = {
            "status": "success" if success else "error",
            "pipeline": "Full CrewAI Pipeline",
            "topic": topic,
            "message": message
        }
        
        if success and result:
            response_data["result"] = result
        
        return jsonify(response_data), 200 if success else 500

    # -------------------------------
    # 🎓 Training/Testing Endpoints (existing)
    # -------------------------------

    @app.route('/train', methods=['POST'])
    def train_route():
        """Train the crew"""
        try:
            data = request.get_json()
            if not data or 'n_iterations' not in data or 'filename' not in data:
                return jsonify({
                    "status": "error",
                    "message": "n_iterations and filename are required"
                }), 400
            
            topic = data.get('topic', 'Real-time Operating System (RTOS)')
            n_iterations = data['n_iterations']
            filename = data['filename']
            current_year = data.get('current_year', str(datetime.now().year))
            
            inputs = {
                "topic": topic,
                'current_year': current_year
            }
            
            TestGemini().crew().train(n_iterations=n_iterations, filename=filename, inputs=inputs)
            
            return jsonify({
                "status": "success",
                "message": f"Training completed for {n_iterations} iterations, results saved to {filename}"
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Training error: {str(e)}"
            }), 500

    @app.route('/test', methods=['POST'])
    def test_route():
        """Test the crew"""
        try:
            data = request.get_json()
            if not data or 'n_iterations' not in data or 'eval_llm' not in data:
                return jsonify({
                    "status": "error",
                    "message": "n_iterations and eval_llm are required"
                }), 400
            
            topic = data.get('topic', 'Automotive Control Unit Testing')
            n_iterations = data['n_iterations']
            eval_llm = data['eval_llm']
            current_year = data.get('current_year', str(datetime.now().year))
            
            inputs = {
                "topic": topic,
                "current_year": current_year
            }
            
            result = TestGemini().crew().test(n_iterations=n_iterations, eval_llm=eval_llm, inputs=inputs)
            
            return jsonify({
                "status": "success",
                "message": f"Testing completed for {n_iterations} iterations using {eval_llm}",
                "result": str(result)
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Testing error: {str(e)}"
            }), 500

    @app.route('/replay', methods=['POST'])
    def replay_route():
        """Replay a task"""
        try:
            data = request.get_json()
            if not data or 'task_id' not in data:
                return jsonify({
                    "status": "error",
                    "message": "task_id is required"
                }), 400
            
            task_id = data['task_id']
            TestGemini().crew().replay(task_id=task_id)
            
            return jsonify({
                "status": "success",
                "message": f"Replay completed for task: {task_id}"
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Replay error: {str(e)}"
            }), 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            return jsonify({
                "status": "healthy",
                "service": "CrewAI Requirements & Testing API",
                "timestamp": datetime.now().isoformat(),
                "version": "2.1.0",
                "available_endpoints": {
                    "individual_agents": ["/requirements", "/test-design", "/test-implementation"],
                    "individual_agents_pdf": ["/requirements/pdf", "/test-design/pdf", "/test-implementation/pdf"],
                    "full_pipeline": ["/run"],
                    "full_pipeline_pdf": ["/run/pdf"],
                    "training": ["/train", "/test", "/replay"]
                }
            })
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            })

    # Get port from environment variable or default to 5067
    port = int(os.environ.get('PORT', 5067))
    logger.info(f"Starting CrewAI API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# -------------------------------
# Optional CLI: train, test, replay (existing)
# -------------------------------
def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        "topic": "Real-time Operating System (RTOS)",
        'current_year': str(datetime.now().year)
    }
    try:
        TestGemini().crew().train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs)
        print(f"Training completed for {sys.argv[2]} iterations, results saved to {sys.argv[3]}")
    except Exception as e:
        raise Exception(f"Error training the crew: {e}")

def replay():
    """Replay the crew execution from a specific task."""
    try:
        TestGemini().crew().replay(task_id=sys.argv[2])
        print(f"Replay completed for task: {sys.argv[2]}")
    except Exception as e:
        raise Exception(f"Error replaying: {e}")

def test():
    """Test the crew execution and returns the results."""
    inputs = {
        "topic": "Automotive Control Unit Testing",
        "current_year": str(datetime.now().year)
    }
    try:
        result = TestGemini().crew().test(n_iterations=int(sys.argv[2]), eval_llm=sys.argv[3], inputs=inputs)
        print(f"Testing completed for {sys.argv[2]} iterations using {sys.argv[3]} as evaluation LLM")
        return result
    except Exception as e:
        raise Exception(f"Error testing the crew: {e}")

# -------------------------------
# 🧭 Main entry
# -------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "run":
            run()  # 🔥 Start Flask app
        elif cmd == "train":
            if len(sys.argv) < 4:
                print("Usage: python main.py train <n_iterations> <filename>")
            else:
                train()
        elif cmd == "replay":
            if len(sys.argv) < 3:
                print("Usage: python main.py replay <task_id>")
            else:
                replay()
        elif cmd == "test":
            if len(sys.argv) < 4:
                print("Usage: python main.py test <n_iterations> <eval_llm>")
            else:
                test()
        else:
            print("Invalid command. Use: run | train | replay | test")
    else:
        # Default behavior: Start Flask app
        print("Starting CrewAI Requirements & Testing API...")
        run()