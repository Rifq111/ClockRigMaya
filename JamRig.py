import maya.cmds as cmds

# =========================
# UTILS
# =========================
def safe_delete(name):
    if cmds.objExists(name):
        cmds.delete(name)

# =========================
# CLEAN
# =========================
safe_delete("clock_RIG")

# =========================
# ROOT
# =========================
rig_grp = cmds.group(em=True, name="clock_RIG")

# =========================
# CONTROLLER
# =========================
ctrl = cmds.circle(
    name="clock_CTRL",
    normal=(0, 0, 1),
    radius=6
)[0]

cmds.parent(ctrl, rig_grp)

# Driver attribute
if not cmds.attributeQuery("time_minutes", node=ctrl, exists=True):
    cmds.addAttr(
        ctrl,
        ln="time_minutes",
        at="double",
        k=True,
        min=0,
        max=720
    )

# Lock transform
for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
    cmds.setAttr(f"{ctrl}.{attr}", lock=True, keyable=False, channelBox=False)

# =========================
# CREATE HAND SYSTEM
# =========================
def create_hand(name, length, width):
    grp = cmds.group(em=True, name=f"{name}_GRP")
    geo = cmds.polyCube(
        name=f"{name}_GEO",
        w=width,
        h=length,
        d=width
    )[0]

    cmds.parent(geo, grp)

    # Move geo up so pivot stays center
    cmds.move(0, length / 2.0, 0, geo, r=True)

    cmds.parent(grp, rig_grp)
    return grp, geo

minute_grp, minute_geo = create_hand("minute_hand", 6, 0.3)
hour_grp, hour_geo     = create_hand("hour_hand", 4, 0.5)

# Freeze GEO only
cmds.makeIdentity(minute_geo, apply=True)
cmds.makeIdentity(hour_geo, apply=True)

# =========================
# NODES (DRIVERS)
# =========================
md_minute = cmds.createNode("multiplyDivide", name="time_to_minute_MD")
md_hour   = cmds.createNode("multiplyDivide", name="time_to_hour_MD")

cmds.setAttr(md_minute + ".input2X", 6)    # 1 minute = 6 deg
cmds.setAttr(md_hour   + ".input2X", 0.5)  # 1 minute = 0.5 deg

# Connect driver
cmds.connectAttr(ctrl + ".time_minutes", md_minute + ".input1X")
cmds.connectAttr(ctrl + ".time_minutes", md_hour   + ".input1X")

cmds.connectAttr(md_minute + ".outputX", minute_grp + ".rotateZ")
cmds.connectAttr(md_hour   + ".outputX", hour_grp   + ".rotateZ")

# =========================
# LOCK HAND CHANNELS
# =========================
for grp in [minute_grp, hour_grp]:
    for attr in ["tx","ty","tz","rx","ry","sx","sy","sz"]:
        cmds.setAttr(f"{grp}.{attr}", lock=True, keyable=False, channelBox=False)

print("✅ Clean Analog Clock Rig Ready for Animation")
