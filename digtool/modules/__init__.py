from typing import Dict, Type
from digtool.modules.base import BaseModule
from digtool.modules.gravatar import GravatarModule
from digtool.modules.site_template import SiteTemplateModule
from digtool.modules.adobe import AdobeModule

def get_all_modules() -> Dict[str, Type[BaseModule]]:
    return {
        "gravatar": GravatarModule,
        "adobe": AdobeModule,
        "site_template": SiteTemplateModule
    }
