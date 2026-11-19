"""crash_instinct shot 3 (5.9-9.4 s, frames 177-281): "...straight for miles. And the only thing beside it is this one tree. But"
NO CUT (references/crash_instinct/shots/s03.md, plan/s03.json PLAN PASS before the build): the same take as shots 1-2, so this script builds
shot 2's take (s02_crash.build_take2) up to frame 281 and adds the camera of shot 3: the aerial over the road (177-231, very slow push),
the descent toward the tree (232-262), the slow drift at the foot of the road (262-281). The planter shrugs (track, frames 255-272).
    blender -b --factory-startup --python s03_aerial.py -- <out.blend> [--res 270x480] [--samples 12] [--still f:out.png ...]"""
import bpy, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s01_plant as S1, s02_crash as S2  # noqa: E402

F0, F1 = 177, 281
A = S1.A
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s03_aerial.blend"

def camera_aerial(cam):
    keys = [(231, (5.6, -50.0, 13.2), (6.0, 80.0, 0.0), 22), (262, (4.0, -22.0, 1.5), (0.3, 0.5, 3.8), 24), (F1, (4.1, -21.3, 1.52), (0.35, 0.6, 3.8), 24)]
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    for fc in (cam.animation_data.action.fcurves if hasattr(cam.animation_data.action, "fcurves") else []):   # the descent eases in and out
        for k in fc.keyframe_points:
            if 231 <= k.co[0] <= 262: k.interpolation = "BEZIER"

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
    S1.F1 = F1; sc.frame_start, sc.frame_end = S1.F0, F1
    rig, cam = S2.build_take2(sc); camera_aerial(cam)
    sc.frame_start = F0
    S1.finish(sc, OUT)

if __name__ == "__main__": main()
