import config

class System:
    def __init__(self, particle):
        self.particle = particle
        self.sampler = Sampler(DT_SAMPLE)
