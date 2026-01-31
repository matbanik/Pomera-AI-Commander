"""Helper functions for AWS Bedrock model integration using boto3.

This module uses boto3's Converse API for reliable AWS Bedrock integration,
following the same pattern as huggingface_helper.py.
"""
import os
import json
from typing import Dict, Any, Optional, Callable, List

# Try to import boto3 - it should be available since we use botocore for SigV4
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


# Model ID to inference profile mapping for models that require cross-region profiles
INFERENCE_PROFILE_MAPPING = {
    # Claude 3.x models
    "anthropic.claude-3-sonnet-20240229-v1:0": "us.anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0": "us.anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0": "us.anthropic.claude-3-opus-20240229-v1:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-haiku-20241022-v1:0": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    
    # Claude 3.7 models
    "anthropic.claude-3-7-sonnet-20250219-v1:0": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    
    # Claude 4.x models
    "anthropic.claude-sonnet-4-20250514-v1:0": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-opus-4-20250514-v1:0": "us.anthropic.claude-opus-4-20250514-v1:0",
    "anthropic.claude-opus-4-1-20250805-v1:0": "us.anthropic.claude-opus-4-1-20250805-v1:0",
    
    # Claude 4.5 models - use GLOBAL inference profiles (cross-region)
    "anthropic.claude-sonnet-4-5-20250929-v1:0": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "anthropic.claude-haiku-4-5-20251001-v1:0": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-opus-4-5-20251101-v1:0": "global.anthropic.claude-opus-4-5-20251101-v1:0",
    
    # DeepSeek models
    "deepseek.deepseek-r1-v1:0": "us.deepseek.deepseek-r1-v1:0",
    
    # Meta Llama models
    "meta.llama3-8b-instruct-v1:0": "us.meta.llama3-8b-instruct-v1:0",
    "meta.llama3-70b-instruct-v1:0": "us.meta.llama3-70b-instruct-v1:0",
    "meta.llama3-1-8b-instruct-v1:0": "us.meta.llama3-1-8b-instruct-v1:0",
    "meta.llama3-1-70b-instruct-v1:0": "us.meta.llama3-1-70b-instruct-v1:0",
    "meta.llama3-1-405b-instruct-v1:0": "us.meta.llama3-1-405b-instruct-v1:0",
    "meta.llama3-2-1b-instruct-v1:0": "us.meta.llama3-2-1b-instruct-v1:0",
    "meta.llama3-2-3b-instruct-v1:0": "us.meta.llama3-2-3b-instruct-v1:0",
    "meta.llama3-2-11b-vision-instruct-v1:0": "us.meta.llama3-2-11b-vision-instruct-v1:0",
    "meta.llama3-2-90b-vision-instruct-v1:0": "us.meta.llama3-2-90b-vision-instruct-v1:0",
    "meta.llama3-3-70b-instruct-v1:0": "us.meta.llama3-3-70b-instruct-v1:0",
    
    # Mistral models
    "mistral.mistral-large-2402-v1:0": "us.mistral.mistral-large-2402-v1:0",
    "mistral.mistral-large-2407-v1:0": "us.mistral.mistral-large-2407-v1:0",
    "mistral.mistral-small-2402-v1:0": "us.mistral.mistral-small-2402-v1:0",
}


def normalize_model_id(model_id: str, region: str, logger) -> str:
    """Normalize model ID to use proper inference profile if needed.
    
    Args:
        model_id: Original model ID
        region: AWS region
        logger: Logger instance
        
    Returns:
        Normalized model ID with inference profile prefix if needed
    """
    # If already has a prefix, return as-is
    if any(model_id.startswith(prefix) for prefix in ['us.', 'eu.', 'apac.', 'global.']):
        logger.debug(f"Model '{model_id}' already has inference profile prefix")
        return model_id
    
    # Check explicit mapping first
    if model_id in INFERENCE_PROFILE_MAPPING:
        mapped_id = INFERENCE_PROFILE_MAPPING[model_id]
        logger.info(f"Mapped model '{model_id}' to inference profile '{mapped_id}'")
        return mapped_id
    
    # Auto-add prefix for providers that require inference profiles
    requires_inference_profile = any(
        model_id.startswith(prefix) for prefix in [
            'anthropic.', 'deepseek.', 'meta.llama', 'mistral.', 'mixtral.'
        ]
    )
    
    if requires_inference_profile:
        # Determine appropriate regional prefix
        if region.startswith('eu-'):
            prefix = 'eu.'
        elif region.startswith('ap-'):
            prefix = 'apac.'
        else:
            prefix = 'us.'
        
        normalized_id = f"{prefix}{model_id}"
        logger.info(f"Auto-adding inference profile prefix: '{model_id}' -> '{normalized_id}'")
        return normalized_id
    
    return model_id


def get_bedrock_client(settings: Dict[str, Any], logger):
    """Create a boto3 Bedrock Runtime client with appropriate credentials.
    
    Args:
        settings: Dictionary containing auth settings
        logger: Logger instance
        
    Returns:
        boto3 bedrock-runtime client
        
    Raises:
        ValueError: If required credentials are missing
        ImportError: If boto3 is not available
    """
    if not BOTO3_AVAILABLE:
        raise ImportError("boto3 is not available. Please install it with: pip install boto3")
    
    auth_method = settings.get("AUTH_METHOD", "api_key")
    region = settings.get("AWS_REGION", "us-east-1")
    
    # Normalize auth method names (handle both display names and internal values)
    is_api_key_auth = auth_method in ["api_key", "API Key (Bearer Token)"]
    is_iam_auth = auth_method in ["iam", "IAM (Explicit Credentials)"]
    is_session_token_auth = auth_method in ["sessionToken", "Session Token (Temporary Credentials)"]
    is_iam_role_auth = auth_method in ["iam_role", "IAM (Implied Credentials)"]
    
    logger.info(f"Creating Bedrock client with auth method: {auth_method}, region: {region}")
    
    if is_api_key_auth:
        # Bearer token auth - set environment variable for boto3
        api_key = settings.get("API_KEY", "")
        if not api_key:
            raise ValueError("AWS Bedrock API Key is required for Bearer token auth")
        
        # boto3 will automatically use this env var for Bearer token auth
        os.environ['AWS_BEARER_TOKEN_BEDROCK'] = api_key
        logger.debug(f"Set AWS_BEARER_TOKEN_BEDROCK environment variable (length: {len(api_key)})")
        
        # Create client - boto3 will use the Bearer token automatically
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )
        
    elif is_iam_auth:
        # IAM explicit credentials
        access_key = settings.get("AWS_ACCESS_KEY_ID", "")
        secret_key = settings.get("AWS_SECRET_ACCESS_KEY", "")
        
        if not access_key or not secret_key:
            raise ValueError("AWS Access Key ID and Secret Access Key are required for IAM auth")
        
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
    elif is_session_token_auth:
        # Session token (temporary credentials)
        access_key = settings.get("AWS_ACCESS_KEY_ID", "")
        secret_key = settings.get("AWS_SECRET_ACCESS_KEY", "")
        session_token = settings.get("AWS_SESSION_TOKEN", "")
        
        if not access_key or not secret_key or not session_token:
            raise ValueError("Access Key, Secret Key, and Session Token are required")
        
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token
        )
        
    elif is_iam_role_auth:
        # IAM implied credentials (from environment, role, or config)
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )
        
    else:
        raise ValueError(f"Unknown auth method: {auth_method}")
    
    return client


def build_converse_params(prompt: str, settings: Dict[str, Any], logger) -> Dict[str, Any]:
    """Build parameters for the Converse API.
    
    Args:
        prompt: User's input prompt
        settings: Model settings
        logger: Logger instance
        
    Returns:
        Dictionary of Converse API parameters
    """
    # Build messages
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    
    # Build system prompt
    system_prompt = settings.get("system_prompt", "").strip()
    
    # Build inference config
    inference_config = {}
    
    max_tokens = settings.get("MAX_OUTPUT_TOKENS", settings.get("max_tokens", "4096"))
    try:
        inference_config["maxTokens"] = int(max_tokens)
    except (ValueError, TypeError):
        inference_config["maxTokens"] = 4096
    
    # Some models (including Claude Opus 4.5) don't allow both temperature AND top_p
    # If both are set, prefer temperature and skip top_p to avoid API error
    temperature = settings.get("temperature")
    top_p = settings.get("top_p")
    
    if temperature:
        try:
            inference_config["temperature"] = float(temperature)
            # Skip top_p when temperature is set to avoid conflict
        except (ValueError, TypeError):
            pass
    elif top_p:
        try:
            inference_config["topP"] = float(top_p)
        except (ValueError, TypeError):
            pass
    
    # Build params dict
    params = {
        "messages": messages,
        "inferenceConfig": inference_config
    }
    
    if system_prompt:
        params["system"] = [{"text": system_prompt}]
    
    logger.debug(f"Converse API params: {json.dumps(params, indent=2)}")
    return params


def process_bedrock_request(
    prompt: str,
    settings: Dict[str, Any],
    update_callback: Optional[Callable[[str], None]],
    logger
) -> Optional[str]:
    """Process AWS Bedrock request using boto3 SDK (non-streaming).
    
    Args:
        prompt: User's input prompt
        settings: Dictionary containing model settings
        update_callback: Function to call with the result or error message
        logger: Logger instance
        
    Returns:
        Response text or None if using callback
    """
    try:
        if not BOTO3_AVAILABLE:
            error_msg = "boto3 is not available. Please install it with: pip install boto3"
            if update_callback:
                update_callback(error_msg)
            return None
        
        # Get model ID and normalize it
        model_id = settings.get("MODEL", "")
        if not model_id:
            error_msg = "No model specified in settings"
            if update_callback:
                update_callback(error_msg)
            return None
        
        region = settings.get("AWS_REGION", "us-east-1")
        model_id = normalize_model_id(model_id, region, logger)
        
        # Create client
        client = get_bedrock_client(settings, logger)
        
        # Build params
        params = build_converse_params(prompt, settings, logger)
        params["modelId"] = model_id
        
        logger.info(f"Calling Bedrock Converse API with model: {model_id}")
        
        # Call Converse API
        response = client.converse(**params)
        
        # Extract response text
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        
        result_text = ""
        for block in content:
            if "text" in block:
                result_text += block["text"]
        
        # Log usage if available
        usage = response.get("usage", {})
        if usage:
            logger.info(f"Token usage - Input: {usage.get('inputTokens', 'N/A')}, Output: {usage.get('outputTokens', 'N/A')}")
        
        if update_callback:
            update_callback(result_text)
        return result_text
        
    except ClientError as e:
        error_msg = format_bedrock_error(e, settings.get("MODEL", ""), logger)
        logger.error(error_msg)
        if update_callback:
            update_callback(error_msg)
        return None
        
    except NoCredentialsError:
        error_msg = "AWS credentials not found. Please configure your credentials in settings."
        logger.error(error_msg)
        if update_callback:
            update_callback(error_msg)
        return None
        
    except Exception as e:
        error_msg = f"AWS Bedrock Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if update_callback:
            update_callback(error_msg)
        return None


def process_bedrock_stream(
    prompt: str,
    settings: Dict[str, Any],
    update_callback: Callable[[str], None],
    logger
) -> None:
    """Process AWS Bedrock request using boto3 SDK with streaming.
    
    Args:
        prompt: User's input prompt
        settings: Dictionary containing model settings
        update_callback: Function to call with each chunk of text
        logger: Logger instance
    """
    try:
        if not BOTO3_AVAILABLE:
            update_callback("boto3 is not available. Please install it with: pip install boto3")
            return
        
        # Get model ID and normalize it
        model_id = settings.get("MODEL", "")
        if not model_id:
            update_callback("No model specified in settings")
            return
        
        region = settings.get("AWS_REGION", "us-east-1")
        model_id = normalize_model_id(model_id, region, logger)
        
        # Create client
        client = get_bedrock_client(settings, logger)
        
        # Build params
        params = build_converse_params(prompt, settings, logger)
        params["modelId"] = model_id
        
        logger.info(f"Calling Bedrock ConverseStream API with model: {model_id}")
        
        # Call ConverseStream API
        response = client.converse_stream(**params)
        
        # Process the event stream
        accumulated_text = ""
        for event in response.get("stream", []):
            # Handle different event types
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"].get("delta", {})
                if "text" in delta:
                    chunk_text = delta["text"]
                    accumulated_text += chunk_text
                    update_callback(chunk_text)
            
            elif "messageStop" in event:
                # Message complete
                logger.debug("Stream complete - messageStop received")
                
            elif "metadata" in event:
                # Usage metadata at end of stream
                usage = event["metadata"].get("usage", {})
                if usage:
                    logger.info(f"Token usage - Input: {usage.get('inputTokens', 'N/A')}, Output: {usage.get('outputTokens', 'N/A')}")
        
        logger.info(f"Streaming complete. Total characters: {len(accumulated_text)}")
        
    except ClientError as e:
        error_msg = format_bedrock_error(e, settings.get("MODEL", ""), logger)
        logger.error(error_msg)
        update_callback(error_msg)
        
    except NoCredentialsError:
        error_msg = "AWS credentials not found. Please configure your credentials in settings."
        logger.error(error_msg)
        update_callback(error_msg)
        
    except EndpointConnectionError as e:
        error_msg = f"Could not connect to AWS Bedrock endpoint. Please check your internet connection and region settings.\n\nError: {str(e)}"
        logger.error(error_msg)
        update_callback(error_msg)
        
    except Exception as e:
        error_msg = f"AWS Bedrock Streaming Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        update_callback(error_msg)


def format_bedrock_error(error: ClientError, model_id: str, logger) -> str:
    """Format AWS Bedrock ClientError into user-friendly message.
    
    Args:
        error: The ClientError exception
        model_id: The model ID that was being used
        logger: Logger instance
        
    Returns:
        Formatted error message
    """
    error_code = error.response.get("Error", {}).get("Code", "Unknown")
    error_message = error.response.get("Error", {}).get("Message", str(error))
    status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", "N/A")
    
    logger.error(f"Bedrock ClientError - Code: {error_code}, Status: {status_code}, Message: {error_message}")
    
    if error_code == "AccessDeniedException" or status_code == 403:
        error_msg = f"AWS Bedrock Access Denied\n\n"
        error_msg += f"Model: {model_id}\n\n"
        error_msg += "This error typically means:\n"
        error_msg += "1. Your credentials don't have permission to access this model\n"
        error_msg += "2. The model is not enabled in your AWS account\n"
        error_msg += "3. The model is not available in your selected region\n\n"
        error_msg += "Solutions:\n"
        error_msg += "1. Check AWS Bedrock Console for model access\n"
        error_msg += "2. Verify IAM permissions include 'bedrock:InvokeModel'\n"
        error_msg += "3. Try 'IAM (Explicit Credentials)' auth if using API Key\n\n"
        error_msg += f"Original error: {error_message}"
        
    elif error_code == "ValidationException" or status_code == 400:
        error_msg = f"AWS Bedrock Validation Error\n\n"
        error_msg += f"Model: {model_id}\n\n"
        
        if "model identifier is invalid" in error_message.lower():
            error_msg += "The model ID format is invalid.\n\n"
            error_msg += "Solutions:\n"
            error_msg += "1. Use 'Refresh Models' to get current model IDs\n"
            error_msg += "2. Try with inference profile prefix (us., global., etc.)\n"
        elif "on-demand throughput isn't supported" in error_message.lower():
            error_msg += "This model requires an inference profile.\n\n"
            error_msg += "Solutions:\n"
            error_msg += f"• Try: us.{model_id}\n"
            error_msg += f"• Or: global.{model_id}\n"
        else:
            error_msg += f"Error: {error_message}\n"
            
    elif error_code == "ThrottlingException" or status_code == 429:
        error_msg = f"AWS Bedrock Rate Limit Exceeded\n\n"
        error_msg += "Your account is being rate limited.\n"
        error_msg += "This may mean your quota is set to 0 or you've exceeded limits.\n\n"
        error_msg += "Solutions:\n"
        error_msg += "1. Wait a few minutes and try again\n"
        error_msg += "2. Check Service Quotas in AWS Console\n"
        error_msg += "3. Request quota increase if quotas are at 0\n\n"
        error_msg += f"Original error: {error_message}"
        
    elif error_code == "ResourceNotFoundException" or status_code == 404:
        error_msg = f"AWS Bedrock Model Not Found\n\n"
        error_msg += f"Model: {model_id}\n\n"
        error_msg += "Solutions:\n"
        error_msg += "1. Use 'Refresh Models' to get current available models\n"
        error_msg += "2. Verify the model is available in your region\n"
        error_msg += "3. Check for typos in the model ID\n\n"
        error_msg += f"Original error: {error_message}"
        
    elif error_code == "ServiceUnavailableException" or status_code == 503:
        error_msg = f"AWS Bedrock Service Unavailable\n\n"
        error_msg += "The service is temporarily unavailable.\n"
        error_msg += "Please try again in a few moments.\n\n"
        error_msg += f"Original error: {error_message}"
        
    else:
        error_msg = f"AWS Bedrock Error ({error_code})\n\n"
        error_msg += f"Model: {model_id}\n"
        error_msg += f"Status: {status_code}\n\n"
        error_msg += f"Message: {error_message}"
    
    return error_msg


def list_available_models(settings: Dict[str, Any], logger) -> List[Dict[str, str]]:
    """List available Bedrock models using boto3.
    
    Args:
        settings: Dictionary containing auth settings
        logger: Logger instance
        
    Returns:
        List of model dictionaries with 'id' and 'name' keys
    """
    try:
        if not BOTO3_AVAILABLE:
            logger.error("boto3 is not available")
            return []
        
        region = settings.get("AWS_REGION", "us-east-1")
        
        # Create bedrock client (not bedrock-runtime) for listing models
        # We need to handle auth differently here
        auth_method = settings.get("AUTH_METHOD", "api_key")
        is_iam_auth = auth_method in ["iam", "IAM (Explicit Credentials)"]
        is_session_token_auth = auth_method in ["sessionToken", "Session Token (Temporary Credentials)"]
        is_iam_role_auth = auth_method in ["iam_role", "IAM (Implied Credentials)"]
        
        if is_iam_auth:
            access_key = settings.get("AWS_ACCESS_KEY_ID", "")
            secret_key = settings.get("AWS_SECRET_ACCESS_KEY", "")
            client = boto3.client(
                service_name="bedrock",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        elif is_session_token_auth:
            access_key = settings.get("AWS_ACCESS_KEY_ID", "")
            secret_key = settings.get("AWS_SECRET_ACCESS_KEY", "")
            session_token = settings.get("AWS_SESSION_TOKEN", "")
            client = boto3.client(
                service_name="bedrock",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token
            )
        else:
            # IAM role or API key - use default credential chain
            client = boto3.client(
                service_name="bedrock",
                region_name=region
            )
        
        # List foundation models
        response = client.list_foundation_models()
        models = []
        
        for model in response.get("modelSummaries", []):
            model_id = model.get("modelId", "")
            model_name = model.get("modelName", model_id)
            provider = model.get("providerName", "Unknown")
            
            models.append({
                "id": model_id,
                "name": f"{provider} - {model_name}",
                "provider": provider
            })
        
        # Also list inference profiles
        try:
            profiles_response = client.list_inference_profiles()
            for profile in profiles_response.get("inferenceProfileSummaries", []):
                profile_id = profile.get("inferenceProfileId", "")
                profile_name = profile.get("inferenceProfileName", profile_id)
                
                models.append({
                    "id": profile_id,
                    "name": f"[Profile] {profile_name}",
                    "provider": "Inference Profile"
                })
        except Exception as e:
            logger.warning(f"Could not list inference profiles: {e}")
        
        logger.info(f"Found {len(models)} Bedrock models/profiles")
        return models
        
    except Exception as e:
        logger.error(f"Error listing Bedrock models: {e}")
        return []
