import re

with open("src/devin_cli/cli.py", "r") as f:
    lines = f.read().splitlines()

# We want to find each `def ..._cmd(...)` block.
# Then, if it contains `resp = ` and doesn't end with `return`, we insert `return resp`.

new_lines = []
i = 0

in_cmd = False
cmd_indent = ""
cmd_has_resp = False
cmd_lines = []

def finish_cmd():
    global cmd_lines, new_lines, cmd_has_resp
    
    if not cmd_lines: return
    
    # check if has resp
    text = "\n".join(cmd_lines)
    if cmd_has_resp and "return" not in cmd_lines[-1]:
        # find the indentation of the last non-empty line
        for l in reversed(cmd_lines):
            if l.strip():
                indent = len(l) - len(l.lstrip())
                break
        else:
            indent = 4
        
        # Don't add if it's already there
        if not cmd_lines[-1].strip().startswith("return"):
            cmd_lines.append(" " * indent + "return resp")
    
    new_lines.extend(cmd_lines)
    cmd_lines = []
    cmd_has_resp = False

while i < len(lines):
    line = lines[i]
    
    if line.startswith("def ") and "_cmd(" in line:
        finish_cmd() # finish previous if any
        in_cmd = True
        cmd_indent = "def"
        cmd_lines.append(line)
    elif in_cmd:
        if line.startswith("def "): # another function started
            finish_cmd()
            in_cmd = True
            cmd_lines.append(line)
        elif line and not line.startswith(" ") and not line.startswith("("):
            # top level code or decorator
            if line.startswith("@"):
                finish_cmd()
                new_lines.append(line)
                in_cmd = False
            else:
                finish_cmd()
                new_lines.append(line)
                in_cmd = False
        else:
            if "resp =" in line or "resp = " in line:
                cmd_has_resp = True
            cmd_lines.append(line)
    else:
        new_lines.append(line)
        
    i += 1

finish_cmd()

with open("src/devin_cli/cli.py", "w") as f:
    f.write("\n".join(new_lines) + "\n")

print("Patched src/devin_cli/cli.py")
