from gym.envs.registration import register

register(
	id='NewCarRacing-v0',
	entry_point='myenv.myenv:CarRacing',
)
