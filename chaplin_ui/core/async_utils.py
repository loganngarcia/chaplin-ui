"""
Async utilities for Chaplin-UI.

This module provides shared async event loop management used across
CLI and Web interfaces.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

logger = logging.getLogger(__name__)


class AsyncEventLoopManager:
    """Manages an async event loop in a background thread.
    
    This class encapsulates the common pattern of running an async event
    loop in a background thread for use with synchronous code.
    
    Attributes:
        loop: The async event loop instance.
        executor: Thread pool executor running the loop.
        typing_condition: AsyncIO condition for sequence coordination.
    """
    
    def __init__(self):
        """Initialize async event loop manager."""
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor.submit(self._run_event_loop)
        self.typing_condition: Optional[asyncio.Condition] = None
        self._init_async_resources()
    
    def _run_event_loop(self) -> None:
        """Run the async event loop in background thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _init_async_resources(self) -> None:
        """Initialize async resources in the async loop."""
        future = asyncio.run_coroutine_threadsafe(
            self._create_async_lock(),
            self.loop
        )
        future.result()  # Wait for completion
    
    async def _create_async_lock(self) -> None:
        """Create asyncio.Lock and Condition in the event loop's context."""
        lock = asyncio.Lock()
        self.typing_condition = asyncio.Condition(lock)
        logger.debug("Async locks initialized")
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the async event loop.
        
        Args:
            wait: Whether to wait for shutdown to complete.
        """
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.executor.shutdown(wait=wait)
        logger.debug("Async event loop shutdown complete")
