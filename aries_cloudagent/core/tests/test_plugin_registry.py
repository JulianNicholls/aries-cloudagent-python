import pytest

from asynctest import TestCase as AsyncTestCase, mock as async_mock

from ...config.injection_context import InjectionContext
from ...utils.classloader import ClassLoader

from ..plugin_registry import PluginRegistry

from ..error import ProtocolDefinitionValidationError

class TestPluginRegistry(AsyncTestCase):
    def setUp(self):
        self.registry = PluginRegistry()

    async def test_setup(self):
        mod_name = "test_mod"
        mod = async_mock.MagicMock()
        mod.__name__ = mod_name
        ctx = async_mock.MagicMock()
        self.registry._plugins[mod_name] = mod
        assert list(self.registry.plugin_names) == [mod_name]
        assert list(self.registry.plugins) == [mod]
        mod.setup = async_mock.CoroutineMock()
        await self.registry.init_context(ctx)
        mod.setup.assert_awaited_once_with(ctx)

    async def test_register_routes(self):
        mod_name = "test_mod"
        mod = async_mock.MagicMock()
        mod.__name__ = mod_name
        app = async_mock.MagicMock()
        self.registry._plugins[mod_name] = mod
        mod.routes.register = async_mock.CoroutineMock()

        with async_mock.patch.object(
            ClassLoader, "load_module", async_mock.MagicMock(return_value=mod.routes)
        ) as load_module:
            await self.registry.register_admin_routes(app)
            load_module.assert_called_once_with(mod_name + ".routes")

        mod.routes.register.assert_awaited_once_with(app)

    async def test_validate_version_not_a_list(self):
        mod_name = "test_mod"
        mod = async_mock.MagicMock()
        mod.__name__ = mod_name

        versions_not_a_list = {}

        with async_mock.patch.object(
            ClassLoader, "load_module", async_mock.MagicMock(return_value=mod.routes)
        ) as load_module:
            with pytest.raises(ProtocolDefinitionValidationError):
                self.registry.validate_version(versions_not_a_list, mod_name)


    async def test_validate_version_list_element_not_an_object(self):
        mod_name = "test_mod"
        mod = async_mock.MagicMock()
        mod.__name__ = mod_name

        versions_not_a_list = [{}, []]

        with async_mock.patch.object(
            ClassLoader, "load_module", async_mock.MagicMock(return_value=mod.routes)
        ) as load_module:
            with pytest.raises(ProtocolDefinitionValidationError):
                self.registry.validate_version(versions_not_a_list, mod_name)


    async def test_validate_version_list_element_empty(self):
        mod_name = "test_mod"
        mod = async_mock.MagicMock()
        mod.__name__ = mod_name

        versions_not_a_list = []

        with async_mock.patch.object(
            ClassLoader, "load_module", async_mock.MagicMock(return_value=mod.routes)
        ) as load_module:
            with pytest.raises(ProtocolDefinitionValidationError):
                self.registry.validate_version(versions_not_a_list, mod_name)


    def test_repr(self):
        assert type(repr(self.registry)) is str
