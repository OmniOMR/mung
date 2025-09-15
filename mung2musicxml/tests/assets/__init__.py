from .assets_impl import AssetExample, ASSETS_DIR

ALL_EXAMPLES = [s() for s in sorted(AssetExample.__subclasses__(), key=lambda x: x.__name__)]
