from crontab import CronTab


class OwncloudCron():

    def __init__(self, config):
        self.config = config
        self.cron = CronTab(user=self.config.cron_user())

    def remove(self):
        print("remove crontab task")

        for job in self.cron.find_command(self.config.cron_user()):
            self.cron.remove(job)
        self.cron.write()

    def create(self):
        print("create crontab task")
        ci_job = self.cron.new(command=self.config.cron_cmd())
        ci_job.setall('*/1 * * * *')
        self.cron.write()