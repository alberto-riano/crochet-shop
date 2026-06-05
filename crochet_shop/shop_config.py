import configparser
from pathlib import Path

_config = None


def get_shop_config():
    """Load and cache shop.conf values."""
    global _config
    if _config is None:
        _config = configparser.ConfigParser()
        conf_path = Path(__file__).resolve().parent.parent / 'shop.conf'
        _config.read(conf_path, encoding='utf-8')
    return _config


def get_payment_config():
    """Return payment-related config as a dict for templates."""
    cfg = get_shop_config()
    return {
        'bizum_telefono': cfg.get('pagos', 'bizum_telefono', fallback=''),
        'banco_iban': cfg.get('pagos', 'banco_iban', fallback=''),
        'banco_beneficiario': cfg.get('pagos', 'banco_beneficiario', fallback=''),
        'banco_entidad': cfg.get('pagos', 'banco_entidad', fallback=''),
    }


def get_shop_info():
    """Return general shop info for templates."""
    cfg = get_shop_config()
    return {
        'nombre': cfg.get('tienda', 'nombre', fallback='Miles de Puntos'),
        'propietaria': cfg.get('tienda', 'propietaria', fallback=''),
        'email_contacto': cfg.get('tienda', 'email_contacto', fallback=''),
        'instagram': cfg.get('redes', 'instagram', fallback=''),
    }
