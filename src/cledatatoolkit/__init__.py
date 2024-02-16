# Expose the other modules as attributes of parent package to give functions some context
# This requires importing top-level package once `cledatatoolkit`, where you access these inner modules keeping it clear where they come from
from . import spatial
from . import property
from . import census