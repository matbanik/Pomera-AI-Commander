"""Helper functions for HuggingFace model integration."""
import json
from typing import Dict, Any, Optional, Union, List
from huggingface_hub import InferenceClient, model_info
from huggingface_hub.utils import HfHubHTTPError

def process_huggingface_request(api_key: str, prompt: str, settings: Dict[str, Any], 
                             update_callback, logger) -> None:
    """Process HuggingFace AI request with proper task handling.
    
    Args:
        api_key: HuggingFace API key
        prompt: User's input prompt
        settings: Dictionary containing model settings
        update_callback: Function to call with the result or error message
        logger: Logger instance for logging
    """
    try:
        # Add timeout configuration for better reliability (default 60 seconds)
        timeout = int(settings.get("timeout", 60))
        client = InferenceClient(token=api_key, timeout=timeout)
        model_name = settings.get("MODEL", "")
        
        if not model_name:
            update_callback("Error: No model specified in settings.")
            return
        
        # Detect supported tasks from HuggingFace API
        logger.info(f"Detecting supported tasks for model: {model_name}")
        supported_tasks = get_model_supported_tasks(model_name, api_key, logger)
        
        if not supported_tasks:
            # Try to determine if this is an API key issue or model name issue
            logger.warning(f"Could not determine supported tasks for model '{model_name}'")
            # Don't return here - let the routing logic handle the fallback
        else:
            logger.info(f"Model '{model_name}' supports tasks: {supported_tasks}")
        

        
        # Route to appropriate handler based on supported tasks
        if "text-classification" in supported_tasks:
            handle_text_classification(client, prompt, model_name, update_callback, logger)
        elif any(task in supported_tasks for task in ["text-generation", "conversational"]):
            handle_chat_completion(client, prompt, model_name, settings, update_callback, logger)
        else:
            # Enhanced model type detection
            is_base_model = detect_base_model(model_name, logger)
            is_chat_model = detect_chat_model(model_name, logger)
            
            if is_chat_model and not is_base_model:
                # Definitely a chat model, try chat completion first
                logger.info(f"Detected chat model '{model_name}', trying chat completion")
                try:
                    handle_chat_completion(client, prompt, model_name, settings, update_callback, logger)
                    return
                except Exception as chat_error:
                    logger.warning(f"Chat completion failed: {chat_error}")
                    
                    # Try text generation as fallback
                    try:
                        logger.info("Attempting text generation as fallback")
                        handle_text_generation(client, prompt, model_name, settings, update_callback, logger)
                        return
                    except Exception as text_gen_fallback_error:
                        logger.warning(f"Text generation fallback failed: {text_gen_fallback_error}")
            
            elif is_base_model or not supported_tasks:
                # Base model or no tasks detected, try text generation first
                logger.info(f"Detected base model or no tasks found for '{model_name}', trying text generation")
                try:
                    handle_text_generation(client, prompt, model_name, settings, update_callback, logger)
                    return
                except Exception as text_gen_error:
                    logger.warning(f"Text generation failed: {text_gen_error}")
                    
                    # Try chat completion as final fallback
                    try:
                        logger.info("Attempting chat completion as final fallback")
                        handle_chat_completion(client, prompt, model_name, settings, update_callback, logger)
                        return
                    except Exception as chat_fallback_error:
                        logger.warning(f"Chat completion fallback failed: {chat_fallback_error}")
            
            else:
                # Unknown model type, try both approaches
                logger.info(f"Unknown model type for '{model_name}', trying both approaches")
                
                # Try text generation first (more common for base models)
                try:
                    handle_text_generation(client, prompt, model_name, settings, update_callback, logger)
                    return
                except Exception as text_gen_error:
                    logger.warning(f"Text generation failed: {text_gen_error}")
                    
                    # Try chat completion as fallback
                    try:
                        logger.info("Attempting chat completion as fallback")
                        handle_chat_completion(client, prompt, model_name, settings, update_callback, logger)
                        return
                    except Exception as chat_fallback_error:
                        logger.warning(f"Chat completion fallback failed: {chat_fallback_error}")
            
            # All methods failed
            error_msg = f"Model '{model_name}' is not supported by HuggingFace Inference API.\n\n"
            
            if "isn't deployed by any Inference Provider" in str(supported_tasks):
                error_msg += "This model is not deployed by any Inference Provider.\n\n"
            
            if supported_tasks:
                error_msg += f"Detected tasks: {', '.join(supported_tasks)}\n\n"
            else:
                error_msg += "Could not determine supported tasks.\n\n"
                
            error_msg += "Solutions:\n"
            error_msg += "1. Try a chat-optimized version (e.g., add '-chat' to model name)\n"
            error_msg += "2. Use a model that's deployed on HuggingFace Inference API\n"
            error_msg += "3. Verify your HuggingFace API key is valid\n"
            error_msg += "4. Check the model page for inference provider availability"
            
            logger.warning(error_msg)
            update_callback(error_msg)
            
    except HfHubHTTPError as e:
        error_msg = format_hf_http_error(e, settings.get("MODEL"))
        logger.error(error_msg, exc_info=True)
        update_callback(error_msg)
    except Exception as e:
        error_msg = format_generic_error(e, settings.get("MODEL"))
        logger.error(error_msg, exc_info=True)
        update_callback(error_msg)

def detect_base_model(model_name: str, logger) -> bool:
    """Detect if a model is a base model (not fine-tuned for chat)."""
    model_lower = model_name.lower()
    
    # Patterns that indicate base models
    base_patterns = [
        '-hf',           # HuggingFace format indicator
        'base',          # Explicitly named base models
        'pretrained',    # Pre-trained models
        'foundation',    # Foundation models
        'raw',           # Raw/untuned models
        'original',      # Original models
    ]
    
    # Patterns that indicate NOT base models (chat/instruct models)
    non_base_patterns = [
        'chat',
        'instruct',
        'assistant',
        'conversation',
        'dialogue',
        'it',            # Instruction tuned
        'sft',           # Supervised fine-tuned
        'dpo',           # Direct preference optimization
        'rlhf',          # Reinforcement learning from human feedback
    ]
    
    # Check for non-base patterns first (these override base patterns)
    has_non_base = any(pattern in model_lower for pattern in non_base_patterns)
    if has_non_base:
        logger.debug(f"Model '{model_name}' has non-base patterns, not a base model")
        return False
    
    # Check for base patterns
    has_base = any(pattern in model_lower for pattern in base_patterns)
    if has_base:
        logger.debug(f"Model '{model_name}' has base patterns, likely a base model")
        return True
    
    # Additional heuristics based on model naming conventions
    # Models without specific suffixes are often base models
    if not any(suffix in model_lower for suffix in ['-chat', '-instruct', '-it', '-sft']):
        # Check if it's a well-known base model pattern
        if any(pattern in model_lower for pattern in ['llama', 'mistral', 'qwen', 'phi']):
            # These are often base models unless explicitly marked otherwise
            logger.debug(f"Model '{model_name}' appears to be a base model based on naming convention")
            return True
    
    logger.debug(f"Model '{model_name}' does not appear to be a base model")
    return False

def detect_chat_model(model_name: str, logger) -> bool:
    """Detect if a model is specifically designed for chat/conversation."""
    model_lower = model_name.lower()
    
    # Patterns that strongly indicate chat models
    chat_patterns = [
        'chat',
        'instruct',
        'assistant',
        'conversation',
        'dialogue',
        'dialog',        # Alternative spelling
        'it',            # Instruction tuned
        'sft',           # Supervised fine-tuned
        'dpo',           # Direct preference optimization
        'rlhf',          # Reinforcement learning from human feedback
        'alpaca',        # Alpaca models are instruction-tuned
        'vicuna',        # Vicuna models are chat-tuned
        'wizard',        # WizardLM models are instruction-tuned
        'dialogpt',      # DialoGPT models are for dialogue
    ]
    
    has_chat_pattern = any(pattern in model_lower for pattern in chat_patterns)
    if has_chat_pattern:
        logger.debug(f"Model '{model_name}' has chat patterns, likely a chat model")
        return True
    
    logger.debug(f"Model '{model_name}' does not appear to be a chat model")
    return False

def get_model_supported_tasks(model_name: str, api_key: str, logger) -> List[str]:
    """Query HuggingFace API to get the supported tasks for a model.
    
    Args:
        model_name: Name of the HuggingFace model
        api_key: HuggingFace API key
        logger: Logger instance
        
    Returns:
        List of supported task names (e.g., ['text-classification', 'text-generation'])
    """
    try:
        info = model_info(model_name, token=api_key)
        
        # Check if this is a LoRA adapter model
        is_lora_adapter = False
        if hasattr(info, 'tags') and info.tags:
            is_lora_adapter = any('lora' in tag.lower() or 'peft' in tag.lower() for tag in info.tags)
        
        # Check model name patterns for LoRA adapters
        if not is_lora_adapter:
            lora_patterns = ['lora', 'peft', 'adapter', 'fingpt']
            is_lora_adapter = any(pattern in model_name.lower() for pattern in lora_patterns)
        
        if is_lora_adapter:
            logger.info(f"Detected LoRA adapter model: {model_name}")
            # LoRA adapters typically don't have inference providers
            # Return empty list to trigger special handling
            return []
        
        # Get pipeline_tag (primary task)
        tasks = []
        if hasattr(info, 'pipeline_tag') and info.pipeline_tag:
            tasks.append(info.pipeline_tag)
            
        # Also check tags for additional supported tasks
        if hasattr(info, 'tags') and info.tags:
            task_tags = [tag for tag in info.tags if any(
                keyword in tag for keyword in 
                ['classification', 'generation', 'conversational', 'sentiment']
            )]
            tasks.extend(task_tags)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tasks = []
        for task in tasks:
            if task not in seen:
                seen.add(task)
                unique_tasks.append(task)
                
        return unique_tasks
        
    except Exception as e:
        logger.warning(f"Could not fetch model info for '{model_name}': {e}")
        return []

def handle_text_classification(client: InferenceClient, prompt: str, model_name: str,
                             update_callback, logger) -> None:
    """Handle text classification models (e.g., sentiment analysis, categorization)."""
    try:
        logger.info(f"Running text classification on model: {model_name}")
        result = client.text_classification(prompt, model=model_name)
        
        # Format the classification results
        if hasattr(result, 'label') and hasattr(result, 'score'):
            response_text = f"Classification Result:\n\nLabel: {result.label}\nConfidence: {result.score:.4f} ({result.score*100:.2f}%)"
        elif isinstance(result, list) and len(result) > 0:
            response_text = "Classification Results:\n\n"
            for i, item in enumerate(result, 1):
                if hasattr(item, 'label') and hasattr(item, 'score'):
                    response_text += f"{i}. {item.label}: {item.score:.4f} ({item.score*100:.2f}%)\n"
                else:
                    response_text += f"{i}. {item}\n"
        else:
            response_text = f"Classification Result:\n\n{str(result)}"
            
        logger.info("Text classification completed successfully")
        update_callback(response_text)
        
    except Exception as e:
        error_msg = f"Text Classification Error: {str(e)}\n\n"
        error_msg += f"Failed to classify text using model '{model_name}'.\n"
        error_msg += "Please verify the model supports text classification and try again."
        logger.error(error_msg, exc_info=True)
        update_callback(error_msg)

def handle_text_generation(client: InferenceClient, prompt: str, model_name: str,
                         settings: Dict[str, Any], update_callback, logger) -> None:
    """Handle text generation models (base models without chat formatting)."""
    try:
        logger.info(f"Running text generation on model: {model_name}")
        
        # Build parameters for text generation
        params = {"model": model_name}
        
        # Add supported parameters
        for param_name, param_type in [
            ("max_new_tokens", int), 
            ("temperature", float), 
            ("top_p", float),
            ("top_k", int),
            ("repetition_penalty", float),
            ("do_sample", bool)
        ]:
            if param_name in settings:
                try:
                    if param_type == bool:
                        # Handle boolean conversion for do_sample
                        if isinstance(settings[param_name], str):
                            params[param_name] = settings[param_name].lower() in ('true', '1', 'yes', 'on')
                        else:
                            params[param_name] = bool(settings[param_name])
                    else:
                        params[param_name] = param_type(settings[param_name])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {param_name} value '{settings[param_name]}' to {param_type}")
        
        # Handle stop sequences
        stop_seq_str = str(settings.get("stop_sequences", '')).strip()
        if stop_seq_str:
            params["stop_sequences"] = [s.strip() for s in stop_seq_str.split(',')]
        
        # Set default parameters if not provided
        if "max_new_tokens" not in params:
            params["max_new_tokens"] = 512
        if "temperature" not in params:
            params["temperature"] = 0.7
        if "do_sample" not in params:
            params["do_sample"] = True
        
        logger.debug(f"HuggingFace text generation payload: {json.dumps(params, indent=2)}")
        
        # Call text generation
        response = client.text_generation(prompt, **params)
        
        # Handle response
        if hasattr(response, 'generated_text'):
            result_text = response.generated_text
        elif isinstance(response, str):
            result_text = response
        else:
            result_text = str(response)
        
        # Clean up the response (remove the original prompt if it's included)
        if result_text.startswith(prompt):
            result_text = result_text[len(prompt):].strip()
        
        logger.info("Text generation completed successfully")
        update_callback(result_text)
        
    except Exception as e:
        error_msg = f"Text Generation Error: {str(e)}\n\n"
        error_msg += f"Failed to generate text using model '{model_name}'.\n"
        
        if "doesn't support task 'text-generation'" in str(e):
            error_msg += "\nThis model doesn't support text generation. It may be a specialized model (e.g., classification, embedding).\n"
            error_msg += "Try using a different model or check the model's documentation for supported tasks."
        elif "isn't deployed by any Inference Provider" in str(e):
            error_msg += "\nThis model is not deployed by any Inference Provider on HuggingFace.\n"
            error_msg += "Solutions:\n"
            error_msg += "1. Try a similar model that's available on the Inference API\n"
            error_msg += "2. Use HuggingFace Spaces or deploy the model yourself\n"
            error_msg += "3. Check the model page for inference provider availability"
        else:
            error_msg += "Please verify the model supports text generation and try again."
        
        logger.error(error_msg, exc_info=True)
        update_callback(error_msg)

def handle_chat_completion(client: InferenceClient, prompt: str, model_name: str, 
                         settings: Dict[str, Any], update_callback, logger) -> None:
    """Handle chat completion models."""
    try:
        messages = []
        system_prompt = settings.get("system_prompt", "").strip()
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {"messages": messages, "model": model_name}
        
        # Add supported parameters
        for param_name, param_type in [
            ("max_tokens", int), 
            ("seed", int), 
            ("temperature", float), 
            ("top_p", float)
        ]:
            if param_name in settings:
                try:
                    params[param_name] = param_type(settings[param_name])
                except (ValueError, TypeError):
                    pass
        
        stop_seq_str = str(settings.get("stop_sequences", '')).strip()
        if stop_seq_str:
            params["stop"] = [s.strip() for s in stop_seq_str.split(',')]
        
        logger.debug(f"HuggingFace chat completion payload: {json.dumps(params, indent=2)}")
        response_obj = client.chat_completion(**params)
        update_callback(response_obj.choices[0].message.content)
        
    except Exception as e:
        error_msg = f"HuggingFace Chat Error: {str(e)}\n\n"
        error_msg += "This model may not support chat completion. Please try a different model or check the model's documentation."
        if "doesn't support task 'conversational'" in str(e):
            error_msg += "\n\nNote: This appears to be a text classification model, not a chat model. It's designed to analyze text and return categories/sentiment, not generate responses."
        logger.error(error_msg, exc_info=True)
        update_callback(error_msg)

def format_hf_http_error(error: HfHubHTTPError, model_name: str = "") -> str:
    """Format HuggingFace HTTP error messages."""
    error_msg = f"HuggingFace API Error: {error.response.status_code} - {error.response.reason}\n\n{error.response.text}"
    
    if error.response.status_code == 401:
        error_msg += "\n\nThis means your API token is invalid or expired. Please check your API key."
    elif error.response.status_code == 403:
        error_msg += f"\n\nThis is a 'gated model'. You MUST accept the terms on the model page:\nhttps://huggingface.co/{model_name}"
    elif error.response.status_code == 404:
        error_msg += "\n\nThe model was not found. Please check the model name and try again."
    
    return error_msg


def format_generic_error(error: Exception, model_name: str = "") -> str:
    """Format generic error messages."""
    error_msg = f"HuggingFace Error: {str(error)}\n\n"
    error_msg += "Please check that the model supports the task you're trying to perform.\n"
    error_msg += f"Model: {model_name or 'Not specified'}\n"
    error_msg += "\nCommon issues:\n"
    error_msg += "1. The model may not support chat completion\n"
    error_msg += "2. The model may require a different task type (e.g., text-classification)\n"
    error_msg += "3. The model may be gated - check if you need to accept terms at https://huggingface.co/models"
    
    return error_msg
