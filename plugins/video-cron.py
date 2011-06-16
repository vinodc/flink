from taino.api import Component
from canarreos.api import ICronJob

class MyCronJob(Component):
    component_id = 'com.flink.app.VideoCron'
    component_description = 'Video cron job'
    implements = [ICronJob,]
    
    def timing(self):
      # Runs every 2 minutes
        return '*/2 * * * *'
    
    def run(self):
        import os
        import settings
        os.system('python manage.py vlprocess 2>&1 1>>'+ settings.LOG_FILENAME)
