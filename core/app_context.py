"""
Application Context - Dependency injection container.

This module provides a centralized container for application dependencies,
enabling better testability, modularity, and clear visibility of dependencies.

Author: Pomera AI Commander Team
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict, Callable, TypeVar, Generic
import logging
import weakref


T = TypeVar('T')


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered."""
    pass


class ServiceAlreadyRegisteredError(Exception):
    """Raised when attempting to register a service that already exists."""
    pass


@dataclass
class ServiceDescriptor:
    """
    Descriptor for a registered service.
    
    Attributes:
        name: Service name/identifier
        instance: The service instance (or None if lazy)
        factory: Factory function for lazy instantiation
        singleton: Whether to cache the instance
        description: Human-readable description
    """
    name: str
    instance: Any = None
    factory: Optional[Callable[[], Any]] = None
    singleton: bool = True
    description: str = ""
    
    @property
    def is_lazy(self) -> bool:
        """Check if this is a lazy-loaded service."""
        return self.factory is not None and self.instance is None


@dataclass
class AppContext:
    """
    Container for application dependencies.
    
    This allows for:
    - Easy testing with mock dependencies
    - Clear visibility of application dependencies
    - Centralized dependency management
    - Lazy loading of services
    
    Usage:
        # Create context
        ctx = AppContext()
        
        # Register services
        ctx.register('logger', logger_instance)
        ctx.register_lazy('database', lambda: DatabaseConnection())
        
        # Get services
        logger = ctx.get('logger')
        db = ctx.get('database')  # Created on first access
        
        # Or use typed properties for common services
        ctx.logger  # Returns logger if registered
    """
    
    # Core services (typed for IDE support)
    logger: Optional[logging.Logger] = None
    settings_manager: Any = None
    dialog_manager: Any = None
    error_service: Any = None
    
    # Processing services
    async_processor: Any = None
    stats_calculator: Any = None
    event_consolidator: Any = None
    
    # Tool management
    tool_loader: Any = None
    widget_cache: Any = None
    
    # UI references (set after UI creation)
    root_window: Any = None
    
    # Internal service registry
    _services: Dict[str, ServiceDescriptor] = field(default_factory=dict)
    _initialized: bool = False
    
    def __post_init__(self):
        """Initialize the service registry."""
        self._services = {}
        self._initialized = True
    
    def register(self, 
                 name: str, 
                 instance: Any, 
                 description: str = "",
                 overwrite: bool = False) -> 'AppContext':
        """
        Register a service instance.
        
        Args:
            name: Service name/identifier
            instance: The service instance
            description: Human-readable description
            overwrite: Allow overwriting existing service
            
        Returns:
            Self for method chaining
            
        Raises:
            ServiceAlreadyRegisteredError: If service exists and overwrite=False
        """
        if name in self._services and not overwrite:
            raise ServiceAlreadyRegisteredError(
                f"Service '{name}' is already registered. Use overwrite=True to replace."
            )
        
        self._services[name] = ServiceDescriptor(
            name=name,
            instance=instance,
            description=description
        )
        
        # Also set typed attribute if it exists
        if hasattr(self, name) and name != '_services':
            setattr(self, name, instance)
        
        return self
    
    def register_lazy(self,
                      name: str,
                      factory: Callable[[], Any],
                      singleton: bool = True,
                      description: str = "",
                      overwrite: bool = False) -> 'AppContext':
        """
        Register a lazy-loaded service.
        
        The factory function is called on first access.
        
        Args:
            name: Service name/identifier
            factory: Factory function that creates the service
            singleton: If True, cache the instance after first creation
            description: Human-readable description
            overwrite: Allow overwriting existing service
            
        Returns:
            Self for method chaining
        """
        if name in self._services and not overwrite:
            raise ServiceAlreadyRegisteredError(
                f"Service '{name}' is already registered. Use overwrite=True to replace."
            )
        
        self._services[name] = ServiceDescriptor(
            name=name,
            factory=factory,
            singleton=singleton,
            description=description
        )
        
        return self
    
    def get(self, name: str, default: Any = None) -> Any:
        """
        Get a registered service.
        
        Args:
            name: Service name/identifier
            default: Default value if service not found
            
        Returns:
            The service instance, or default if not found
        """
        if name not in self._services:
            # Check typed attributes
            if hasattr(self, name):
                value = getattr(self, name)
                if value is not None:
                    return value
            return default
        
        descriptor = self._services[name]
        
        # Return existing instance
        if descriptor.instance is not None:
            return descriptor.instance
        
        # Lazy instantiation
        if descriptor.factory is not None:
            instance = descriptor.factory()
            
            if descriptor.singleton:
                descriptor.instance = instance
                # Also set typed attribute if it exists
                if hasattr(self, name) and name != '_services':
                    setattr(self, name, instance)
            
            return instance
        
        return default
    
    def get_required(self, name: str) -> Any:
        """
        Get a required service (raises if not found).
        
        Args:
            name: Service name/identifier
            
        Returns:
            The service instance
            
        Raises:
            ServiceNotFoundError: If service is not registered
        """
        result = self.get(name)
        if result is None:
            raise ServiceNotFoundError(f"Required service '{name}' not found")
        return result
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name/identifier
            
        Returns:
            True if service is registered
        """
        if name in self._services:
            return True
        if hasattr(self, name):
            return getattr(self, name) is not None
        return False
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a service.
        
        Args:
            name: Service name/identifier
            
        Returns:
            True if service was removed, False if not found
        """
        if name in self._services:
            del self._services[name]
            if hasattr(self, name) and name != '_services':
                setattr(self, name, None)
            return True
        return False
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered services.
        
        Returns:
            Dictionary with service info
        """
        result = {}
        
        for name, descriptor in self._services.items():
            result[name] = {
                'registered': True,
                'instantiated': descriptor.instance is not None,
                'lazy': descriptor.is_lazy,
                'singleton': descriptor.singleton,
                'description': descriptor.description
            }
        
        return result
    
    def is_initialized(self) -> bool:
        """
        Check if essential services are initialized.
        
        Returns:
            True if logger and settings_manager are available
        """
        return (
            self.logger is not None and
            self.settings_manager is not None
        )
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        
        # Reset typed attributes
        self.logger = None
        self.settings_manager = None
        self.dialog_manager = None
        self.error_service = None
        self.async_processor = None
        self.stats_calculator = None
        self.event_consolidator = None
        self.tool_loader = None
        self.widget_cache = None
        self.root_window = None


class AppContextBuilder:
    """
    Builder for creating AppContext with proper initialization order.
    
    Usage:
        context = (AppContextBuilder()
            .with_logger(logger)
            .with_settings_manager(settings_mgr)
            .with_dialog_manager(dialog_mgr)
            .with_error_service(error_svc)
            .build())
    """
    
    def __init__(self):
        self._context = AppContext()
    
    def with_logger(self, logger: logging.Logger) -> 'AppContextBuilder':
        """Add logger to context."""
        self._context.logger = logger
        self._context.register('logger', logger, 'Application logger')
        return self
    
    def with_settings_manager(self, manager: Any) -> 'AppContextBuilder':
        """Add settings manager to context."""
        self._context.settings_manager = manager
        self._context.register('settings_manager', manager, 'Settings manager')
        return self
    
    def with_dialog_manager(self, manager: Any) -> 'AppContextBuilder':
        """Add dialog manager to context."""
        self._context.dialog_manager = manager
        self._context.register('dialog_manager', manager, 'Dialog manager')
        return self
    
    def with_error_service(self, service: Any) -> 'AppContextBuilder':
        """Add error service to context."""
        self._context.error_service = service
        self._context.register('error_service', service, 'Error handling service')
        return self
    
    def with_async_processor(self, processor: Any) -> 'AppContextBuilder':
        """Add async processor to context."""
        self._context.async_processor = processor
        self._context.register('async_processor', processor, 'Async text processor')
        return self
    
    def with_stats_calculator(self, calculator: Any) -> 'AppContextBuilder':
        """Add stats calculator to context."""
        self._context.stats_calculator = calculator
        self._context.register('stats_calculator', calculator, 'Statistics calculator')
        return self
    
    def with_event_consolidator(self, consolidator: Any) -> 'AppContextBuilder':
        """Add event consolidator to context."""
        self._context.event_consolidator = consolidator
        self._context.register('event_consolidator', consolidator, 'Event consolidator')
        return self
    
    def with_tool_loader(self, loader: Any) -> 'AppContextBuilder':
        """Add tool loader to context."""
        self._context.tool_loader = loader
        self._context.register('tool_loader', loader, 'Tool loader')
        return self
    
    def with_widget_cache(self, cache: Any) -> 'AppContextBuilder':
        """Add widget cache to context."""
        self._context.widget_cache = cache
        self._context.register('widget_cache', cache, 'Widget cache')
        return self
    
    def with_root_window(self, window: Any) -> 'AppContextBuilder':
        """Add root window reference to context."""
        self._context.root_window = window
        self._context.register('root_window', window, 'Root Tkinter window')
        return self
    
    def with_service(self, 
                     name: str, 
                     instance: Any, 
                     description: str = "") -> 'AppContextBuilder':
        """Add a custom service to context."""
        self._context.register(name, instance, description)
        return self
    
    def with_lazy_service(self,
                          name: str,
                          factory: Callable[[], Any],
                          singleton: bool = True,
                          description: str = "") -> 'AppContextBuilder':
        """Add a lazy-loaded service to context."""
        self._context.register_lazy(name, factory, singleton, description)
        return self
    
    def build(self) -> AppContext:
        """
        Build and return the configured AppContext.
        
        Returns:
            Configured AppContext instance
        """
        return self._context


# Global context instance
_app_context: Optional[AppContext] = None


def get_app_context() -> Optional[AppContext]:
    """
    Get the global application context.
    
    Returns:
        The global AppContext instance, or None if not initialized
    """
    return _app_context


def set_app_context(context: AppContext) -> None:
    """
    Set the global application context.
    
    Args:
        context: The AppContext to set as global
    """
    global _app_context
    _app_context = context


def create_app_context() -> AppContext:
    """
    Create a new AppContext and set it as the global instance.
    
    Returns:
        New AppContext instance
    """
    global _app_context
    _app_context = AppContext()
    return _app_context


def clear_app_context() -> None:
    """Clear the global application context."""
    global _app_context
    if _app_context is not None:
        _app_context.clear()
    _app_context = None


def require_context() -> AppContext:
    """
    Get the global context, raising if not initialized.
    
    Returns:
        The global AppContext
        
    Raises:
        RuntimeError: If context is not initialized
    """
    if _app_context is None:
        raise RuntimeError(
            "Application context not initialized. "
            "Call create_app_context() or set_app_context() first."
        )
    return _app_context

