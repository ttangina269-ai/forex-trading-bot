# Main entry point for forex trading bot

import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
import click
import yaml

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {config_path}: {e}")
        raise


@click.group()
def cli():
    """Forex Trading Bot - Mechanical strategy with strict risk management."""
    pass


@cli.command()
@click.option('--config', default='config/config.yaml',
              help='Configuration file path')
def verify(config):
    """Verify broker connection and configuration."""
    logger.info("Starting connection verification...")
    
    try:
        # Load configuration
        cfg = load_config(config)
        logger.info(f"✓ Configuration loaded: {config}")
        
        # Verify environment variables
        import os
        api_token = os.getenv('OANDA_API_TOKEN')
        account_id = os.getenv('OANDA_ACCOUNT_ID')
        environment = os.getenv('OANDA_ENVIRONMENT', 'practice')
        
        if not api_token:
            logger.error("✗ OANDA_API_TOKEN not set in .env")
            sys.exit(1)
        
        if not account_id:
            logger.error("✗ OANDA_ACCOUNT_ID not set in .env")
            sys.exit(1)
        
        logger.info(f"✓ API Token: {api_token[:20]}...")
        logger.info(f"✓ Account ID: {account_id}")
        logger.info(f"✓ Environment: {environment}")
        
        # TODO: Test actual broker connection when OANDA provider implemented
        logger.info("\n✓ All verifications passed!")
        logger.info(f"  Mode: {cfg.get('mode', 'paper')}")
        logger.info(f"  Symbols: {', '.join(cfg.get('trading', {}).get('symbols', []))}")
        logger.info(f"  Risk per trade: {cfg.get('risk_management', {}).get('risk_per_trade', 0.005)*100:.1f}%")
        
    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config', default='config/config.yaml',
              help='Configuration file path')
@click.option('--mode', type=click.Choice(['paper', 'demo', 'live']),
              default='paper', help='Trading mode')
def paper(config, mode):
    """Run bot in paper trading mode."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Forex Trading Bot - {mode.upper()} MODE")
    logger.info(f"{'='*60}\n")
    
    try:
        cfg = load_config(config)
        
        # Verify mode matches config
        if cfg.get('mode') != mode:
            logger.warning(f"Config mode '{cfg.get('mode')}' overridden to '{mode}'")
            cfg['mode'] = mode
        
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Trading symbols: {cfg.get('trading', {}).get('symbols', [])}")
        logger.info(f"Max positions: {cfg.get('trading', {}).get('max_positions', 1)}")
        logger.info(f"Risk per trade: {cfg.get('risk_management', {}).get('risk_per_trade', 0.005)*100:.1f}%")
        logger.info(f"Max daily loss: {cfg.get('risk_management', {}).get('max_daily_loss_pct', 0.02)*100:.1f}%")
        logger.info(f"Max drawdown: {cfg.get('risk_management', {}).get('max_drawdown_pct', 0.15)*100:.1f}%")
        logger.info(f"\nBot starting in {mode.upper()} mode...")
        logger.info("Waiting for market signals...\n")
        
        # TODO: Initialize bot and run main loop when all components implemented
        # For now, just show configuration loaded successfully
        logger.info("✓ Bot ready (awaiting full implementation)")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option('--config', default='config/config.yaml',
              help='Configuration file path')
@click.option('--from', 'from_date', required=True,
              help='Start date (YYYY-MM-DD)')
@click.option('--to', 'to_date', required=True,
              help='End date (YYYY-MM-DD)')
@click.option('--symbols', default=None,
              help='Comma-separated symbols to backtest')
def backtest(config, from_date, to_date, symbols):
    """Run backtesting on historical data."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Forex Trading Bot - BACKTEST MODE")
    logger.info(f"{'='*60}\n")
    
    try:
        cfg = load_config(config)
        
        logger.info(f"Backtest period: {from_date} to {to_date}")
        
        if symbols:
            test_symbols = symbols.split(',')
            logger.info(f"Testing symbols: {test_symbols}")
        else:
            test_symbols = cfg.get('trading', {}).get('symbols', [])
            logger.info(f"Testing symbols: {test_symbols}")
        
        logger.info(f"\nBacktesting strategy with configuration:")
        logger.info(f"  Trend EMA: {cfg.get('indicators', {}).get('ema_trend', 200)}")
        logger.info(f"  Fast EMA: {cfg.get('indicators', {}).get('ema_fast', 20)}")
        logger.info(f"  Slow EMA: {cfg.get('indicators', {}).get('ema_slow', 50)}")
        logger.info(f"  Risk/Reward: 1:{cfg.get('risk_management', {}).get('risk_reward_ratio', 2.0)}")
        logger.info(f"\nLoading historical data...")
        
        # TODO: Implement backtesting engine
        logger.info("✓ Backtest ready (awaiting full implementation)")
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
def test():
    """Run unit tests."""
    logger.info("Running unit tests...")
    import subprocess
    result = subprocess.run(['pytest', 'tests/', '-v'], cwd=Path(__file__).parent.parent)
    sys.exit(result.returncode)


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
