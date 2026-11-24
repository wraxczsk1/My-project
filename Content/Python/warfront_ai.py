
import json
import urllib.request
import re

URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:8b"

SYSTEM = """
Jsi Warfront AI Builder pro Unreal Engine 5.8.
Odpovidej cesky.
Vratis JSON:
{
 "reply": "odpoved",
 "actions": []
}
Povolene akce:
cube: {"type":"cube","location":[0,0,100]}
light: {"type":"light","location":[0,0,200]}
camera: {"type":"camera","location":[500,0,300]}
"""

def ask_qwen(prompt):
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": str(prompt)}
        ]
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    content = result["message"]["content"]
    match = re.search(r"\{.*\}", content, re.S)

    if not match:
        return {"reply": content, "actions": []}

    return json.loads(match.group(0))


def ask(prompt):
    result = ask_qwen(prompt)

    print("WARFRONT AI:", result.get("reply", ""))

    return result


def execute_confirmed(actions):
    try:
        import unreal
    except ImportError:
        raise RuntimeError(
            "Tuto funkci spust pouze uvnitr Unreal Editoru."
        )

    if not isinstance(actions, list) or len(actions) > 20:
        raise ValueError("Neplatny seznam akci")

    results = []

    for action in actions:
        kind = action.get("type")
        pos = action.get("location", [0, 0, 0])

        if not isinstance(pos, list) or len(pos) != 3:
            raise ValueError("Neplatna pozice")

        location = unreal.Vector(*[float(x) for x in pos])

        if kind == "cube":
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor, location
            )

            mesh = unreal.load_object(
                None, "/Engine/BasicShapes/Cube.Cube"
            )

            if not actor or not mesh:
                raise RuntimeError("Cube creation failed")

            actor.static_mesh_component.set_static_mesh(mesh)
            results.append("Cube created")

        elif kind == "light":
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PointLight, location
            )
            if not actor:
                raise RuntimeError("Light creation failed")
            results.append("Light created")

        elif kind == "camera":
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.CameraActor, location
            )
            if not actor:
                raise RuntimeError("Camera creation failed")
            results.append("Camera created")

        else:
            raise ValueError("Nepovolena akce")

    return results


def test_connection():
    result = ask_qwen("Napis cesky: Warfront AI funguje.")
    print("QWEN ONLINE:", result.get("reply"))
    return result


if __name__ == "__main__":
    test_connection()
