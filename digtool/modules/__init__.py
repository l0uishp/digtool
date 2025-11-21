from typing import Dict, Type
from digtool.modules.base import BaseModule
from digtool.modules.gravatar import GravatarModule
from digtool.modules.site_template import SiteTemplateModule
from digtool.modules.adobe import AdobeModule
from digtool.modules.google import GoogleModule

def get_all_modules() -> Dict[str, Type[BaseModule]]:
    return {
        "gravatar": GravatarModule,
        "adobe": AdobeModule,
        "google": GoogleModule,
        "site_template": SiteTemplateModule
    }
