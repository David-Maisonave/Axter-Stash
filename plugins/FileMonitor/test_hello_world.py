import sys, os, pathlib, json

Args = ""
if len(sys.argv) > 1:
    Args = sys.argv[1:]
print(f"StdErr: Hello, world from Python script!\nArgs={Args}", file=sys.stderr)

testFileToCreate = f"{pathlib.Path(__file__).resolve().parent}{os.sep}MyDummyFileFromPython_{pathlib.Path(__file__).stem}.txt"

pathlib.Path(testFileToCreate).touch()

print(f"Hello, world from Python script!\nArgs={Args}")

sys.exit(0)