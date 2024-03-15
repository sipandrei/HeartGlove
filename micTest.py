import pvrhino
from pvrecorder import PvRecorder
import env

# Variabile pentru input audio și Picovoice
devices = PvRecorder.get_available_devices()
print(devices)
ACCESS_KEY = f"{env.access_key}"
CONTEXT_PATH = f"{env.context_path}"
print(f'{ACCESS_KEY}')
print(CONTEXT_PATH)

try:
	rhino = pvrhino.create(access_key=ACCESS_KEY,context_path=CONTEXT_PATH, sensitivity=0.5,endpoint_duration_sec=1.0, require_endpoint=True)
except pvrhino.RhinoInvalidArgumentError as e:
        print("One or more arguments provided to Rhino is invalid: ", args)
        print(e)
        raise e
except pvrhino.RhinoActivationError as e:
        print("AccessKey activation error")
        raise e
except pvrhino.RhinoActivationLimitError as e:
        print("AccessKey '%s' has reached it's temporary device limit" % args.access_key)
        raise e
except pvrhino.RhinoActivationRefusedError as e:
        print("AccessKey '%s' refused" % args.access_key)
        raise e
except pvrhino.RhinoActivationThrottledError as e:
        print("AccessKey '%s' has been throttled" % args.access_key)
        raise e
except pvrhino.RhinoError as e:
        print("Failed to initialize Rhino")
        raise e

recorder = PvRecorder(frame_length=rhino.frame_length, device_index=2)
recorder.start()

def get_next_audio_frame():
  return recorder.read()

def sti():
  intent = ""
  audio_frame = get_next_audio_frame() # preluare audio
  is_finalized = rhino.process(get_next_audio_frame())
  if is_finalized:
    inference = rhino.get_inference()
    understood = inference.is_understood
    if understood: # verificare echivalenta input cu valorile definite
      intent = inference.intent
      slots = inference.slots
  return intent # transmitere numele valorii echivalente

def sti2():
  global recorder, rhino
  pcm = recorder.read()
  is_finalized = rhino.process(pcm)
  if is_finalized:
    inference = rhino.get_inference()
    if inference.is_understood:
      return inference.intent

def dateVictima():
  intent = sti2()
  if intent == "adult" or intent == "child" or intent == "babyVictim":
    return intent
  return ""

try:
  while True:
    var = dateVictima()
    if var != "":
      print(var)
except KeyboardInterrupt:
  print("Stopping...")
finally:
  recorder.delete()
  rhino.delete()
