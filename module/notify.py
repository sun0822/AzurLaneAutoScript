import yaml
import onepush.core
from onepush import get_notifier
from onepush.core import Provider
from onepush.exceptions import OnePushException

from module.logger import logger

onepush.core.log = logger


def handle_notify(_config: str, **kwargs) -> bool:
    try:
        config = {}
        for item in yaml.safe_load_all(_config):
            config.update(item)
    except Exception:
        logger.error("Fail to load onepush config, skip sending")
        return False
    try:
        provider_name = config.pop("provider", None)
        if provider_name is None:
            logger.info("No provider specified, skip sending")
            return False
        notifier: Provider = get_notifier(provider_name)
        required: list[str] = notifier.params["required"]
        config.update(kwargs)

        # pre check
        for key in required:
            if key not in config:
                logger.warning(
                    f"Notifier {notifier.name} require param '{key}' but not provided"
                )

        notifier.notify(**config)
    except OnePushException:
        logger.exception("Push notify failed")
        return False
    except Exception as e:
        logger.exception(e)
        return False

    logger.info("Push notify success")
    return True