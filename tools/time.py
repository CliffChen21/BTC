from datetime import datetime, timedelta


class Time:
    '''
    Input: UTC TimeStamp
    '''

    def __init__(self, time=None, timezone='utc'):
        if isinstance(time, datetime):
            self.time = time.timestamp()
        elif isinstance(time, float):
            self.time = time
        self.timezone = timezone

    @classmethod
    def get_now(cls):
        return Time(datetime.utcnow().timestamp(), 'utc')

    @classmethod
    def get_from_deribit(self, time):
        return Time(time / 1000, "utc")

    # Local
    @property
    def get_local_dt(self):
        if self.timezone == 'utc':
            return datetime.fromtimestamp(self.time) + timedelta(hours=8)
        else:
            if self.timezone.find('+') != -1:
                _, td = self.timezone.split('+')
                return datetime.fromtimestamp(self.time) + timedelta(hours=int(td))
            else:
                _, td = self.timezone.split('-')
                return datetime.fromtimestamp(self.time) - timedelta(hours=int(td))

    @property
    def get_local_ts(self):
        return self.get_local_dt.timestamp()

    @property
    def get_excel_local(self):
        return Time.get_excel(self.get_local_dt)

    @staticmethod
    def get_excel(date):
        temp = datetime(1899, 12, 30)  # Note, not 31st Dec but 30th!
        delta = date - temp
        return float(delta.days) + (float(delta.seconds) / 86400)

    # Deribit
    @property
    def get_deribit_ts(self):
        return int(self.get_deribit_dt.timestamp() * 1000)

    @property
    def get_deribit_dt(self):
        return self.get_local_dt - timedelta(hours=8)


if "__main__" == __name__:
    t = Time(Time.get_now().time, 'utc+8')
    print(t.time)
    print(t.get_local_dt)
    print(t.get_deribit_dt)
