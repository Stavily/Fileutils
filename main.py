#!/usr/bin/env python3
"""File Utils Plugin - Main entry point"""

import argparse
import json
import logging
import sys
from typing import Dict, Any, List
import os
import shutil
from datetime import datetime

# Import shared agent client
sys.path.insert(0, os.path.dirname(__file__))
from stavily_agent_client import StavilyAgentClient, StavilyAgentError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileUtilsPlugin:
    """Main plugin class for file utilities"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the file utils plugin

        Args:
            config: Configuration dictionary from plugin.yaml
        """
        self.config = config

        # Initialize agent client
        self.agent_client = None
        try:
            self.agent_client = StavilyAgentClient()
            self.agent_client.connect()
            logger.info("Connected to Stavily agent")
        except StavilyAgentError as e:
            raise f"Failed to connect to agent: {e}"
        except Exception as e:
            raise f"Unexpected error connecting to agent: {e}"

        logger.info("Initialized File Utils plugin")

    def perform_operation(self) -> Dict[str, Any]:
        """
        Perform a single file operation based on configuration

        Returns:
            Dictionary containing operation result
        """
        operation = self.config.get('operation')
        destination = self.config.get('destination')
        source = self.config.get('source')
        content = self.config.get('content', '')

        result = {
            'operation': operation,
            'destination': destination,
            'success': False,
            'error': None
        }

        if operation == 'create_file':
            result['success'] = self.create_file(destination, content)
        elif operation == 'create_dir':
            result['success'] = self.create_dir(destination)
        elif operation == 'move':
            if source:
                result['source'] = source
                result['success'] = self.move(source, destination)
            else:
                result['error'] = 'Source path required for move operation'
        elif operation == 'delete':
            result['success'] = self.delete(destination)
        elif operation == 'rename':
            if source:
                result['source'] = source
                result['success'] = self.rename(source, destination)
            else:
                result['error'] = 'Source path required for rename operation'
        else:
            result['error'] = f'Unknown operation: {operation}'

        if not result['success'] and not result['error']:
            result['error'] = 'Operation failed'

        return result

    def create_file(self, path: str, content: str = "") -> bool:
        """Create a new file with optional content"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            logger.info(f"Created file: {path}")

            # Report to agent if connected
            if self.agent_client and self.agent_client.is_connected():
                try:
                    self.agent_client.upload_logs([{
                        "level": "INFO",
                        "message": f"Created file: {path}",
                        "timestamp": datetime.now().isoformat()
                    }])
                except StavilyAgentError as e:
                    logger.warning(f"Failed to report file creation to agent: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to create file {path}: {str(e)}")

            # Report error to agent if connected
            if self.agent_client and self.agent_client.is_connected():
                try:
                    self.agent_client.upload_logs([{
                        "level": "ERROR",
                        "message": f"Failed to create file {path}: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }])
                except StavilyAgentError as e:
                    logger.warning(f"Failed to report file creation error to agent: {e}")

            return False

    def create_dir(self, path: str) -> bool:
        """Create a new directory"""
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created directory: {path}")

            # Report to agent if connected
            if self.agent_client and self.agent_client.is_connected():
                try:
                    self.agent_client.upload_logs([{
                        "level": "INFO",
                        "message": f"Created directory: {path}",
                        "timestamp": datetime.now().isoformat()
                    }])
                except StavilyAgentError as e:
                    logger.warning(f"Failed to report directory creation to agent: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {str(e)}")

            # Report error to agent if connected
            if self.agent_client and self.agent_client.is_connected():
                try:
                    self.agent_client.upload_logs([{
                        "level": "ERROR",
                        "message": f"Failed to create directory {path}: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }])
                except StavilyAgentError as e:
                    logger.warning(f"Failed to report directory creation error to agent: {e}")

            return False

    def move(self, source: str, destination: str) -> bool:
        """Move a file or directory"""
        logger.warning(f"Move operation: {source} -> {destination} (WARNING: This operation modifies filesystem)")
        raise(UserWarning("This operation is potentially destructive. Thus, it is disabled by default. Enable it only if you understand the risks."))
        try:
            shutil.move(source, destination)
            logger.info(f"Moved {source} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to move {source} to {destination}: {str(e)}")
            return False

    def delete(self, path: str) -> bool:
        """Delete a file or directory"""
        logger.warning(f"Delete operation: {path} (WARNING: This operation is destructive and cannot be undone)")
        raise(UserWarning("This operation is potentially destructive. Thus, it is disabled by default. Enable it only if you understand the risks."))
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.info(f"Deleted file: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logger.info(f"Deleted directory: {path}")
            else:
                logger.warning(f"Path does not exist: {path}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to delete {path}: {str(e)}")
            return False

    def rename(self, source: str, destination: str) -> bool:
        """Rename a file or directory"""
        logger.warning(f"Rename operation: {source} -> {destination} (WARNING: This operation modifies filesystem)")
        raise(UserWarning("This operation is potentially destructive. Thus, it is disabled by default. Enable it only if you understand the risks."))
        try:
            os.rename(source, destination)
            logger.info(f"Renamed {source} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to rename {source} to {destination}: {str(e)}")
            return False

    def perform_operations(self) -> Dict[str, Any]:
        """
        Perform file operations based on configuration

        Returns:
            Dictionary containing operation results
        """
        operations = self.config.get('operation', [])
        destinations = self.config.get('destination', [])
        sources = self.config.get('source', [])
        contents = self.config.get('content', [])

        results = []
        max_ops = max(len(operations), len(destinations))

        for i in range(max_ops):
            operation = operations[i] if i < len(operations) else None
            destination = destinations[i] if i < len(destinations) else None
            source = sources[i] if i < len(sources) else None
            content = contents[i] if i < len(contents) else ''

            result = {
                'operation': operation,
                'destination': destination,
                'success': False,
                'error': None
            }

            if not operation or not destination:
                result['error'] = 'Operation and destination are required'
            elif operation == 'create_file':
                result['success'] = self.create_file(destination, content)
            elif operation == 'create_dir':
                result['success'] = self.create_dir(destination)
            elif operation == 'move':
                if source:
                    result['source'] = source
                    result['success'] = self.move(source, destination)
                else:
                    result['error'] = 'Source path required for move operation'
            elif operation == 'delete':
                result['success'] = self.delete(destination)
            elif operation == 'rename':
                if source:
                    result['source'] = source
                    result['success'] = self.rename(source, destination)
                else:
                    result['error'] = 'Source path required for rename operation'
            else:
                result['error'] = f'Unknown operation: {operation}'

            if not result['success'] and not result['error']:
                result['error'] = 'Operation failed'

            results.append(result)

        return {
            'total_operations': len(results),
            'successful_operations': sum(1 for r in results if r['success']),
            'failed_operations': sum(1 for r in results if not r['success']),
            'results': results
        }


def main():
    """Main entry point for the plugin"""
    try:
        parser = argparse.ArgumentParser(description='File Utils Plugin')
        parser.add_argument('--operation', nargs='+', choices=['create_file', 'create_dir', 'move', 'delete', 'rename'], help='Operations to perform')
        parser.add_argument('--source', nargs='*', help='Source paths for move/rename operations')
        parser.add_argument('--destination', nargs='+', required=True, help='Destination paths for operations')
        parser.add_argument('--content', nargs='*', help='Content for create_file operations')

        args = parser.parse_args()

        # Build configuration from command line arguments
        config = {
            'operation': args.operation,
            'destination': args.destination,
            'source': args.source or [],
            'content': args.content or []
        }

        # Initialize plugin
        plugin = FileUtilsPlugin(config)

        # Log plugin start to agent
        if plugin.agent_client and plugin.agent_client.is_connected():
            try:
                plugin.agent_client.upload_logs([{
                    "level": "INFO",
                    "message": "File Utils plugin started",
                    "timestamp": datetime.now().isoformat()
                }])
            except StavilyAgentError as e:
                logger.warning(f"Failed to log plugin start to agent: {e}")

        # Perform operations
        result = plugin.perform_operations()

        # Log completion to agent
        if plugin.agent_client and plugin.agent_client.is_connected():
            try:
                status = "success" if result['failed_operations'] == 0 else "partial"
                plugin.agent_client.upload_logs([{
                    "level": "INFO",
                    "message": f"File Utils plugin completed with status: {status}",
                    "timestamp": datetime.now().isoformat()
                }])
            except StavilyAgentError as e:
                logger.warning(f"Failed to log plugin completion to agent: {e}")

        # Output result
        output = {
            'status': 'success' if result['failed_operations'] == 0 else 'partial',
            'data': result
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    except Exception as e:
        logger.error(f"Plugin execution failed: {str(e)}")

        # Log error to agent if possible
        try:
            if 'plugin' in locals() and plugin.agent_client and plugin.agent_client.is_connected():
                plugin.agent_client.upload_logs([{
                    "level": "ERROR",
                    "message": f"File Utils plugin execution failed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }])
        except:
            pass  # Ignore agent logging errors during exception handling

        result = {
            'status': 'error',
            'message': f'Plugin execution failed: {str(e)}'
        }
        print(json.dumps(result))
        sys.exit(1)


if __name__ == '__main__':
    main()