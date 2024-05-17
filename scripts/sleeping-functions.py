import json

def is_void(sign):
    return (sign.startswith("static inline void") or 
                sign.startswith("inline void") or
                sign.startswith("static void") or
                sign.startswith("void") and 
                not sign.startswith("static inline void *")
                and not sign.startswith("static void *")
                and not sign.startswith("void *")
                and not sign.startswith("inline void *"))

build_base_path = "/home/as/Downloads/build-base-linux-5.10.120-x86_64-allmodconfig/"

# FIXME: probably may be found in build_base files
path_in_build_base = "/home/ldvuser/build-bases/linux-5.10.120/"
depth = 2
# FIXME: probably paths may be found in build_base files
funcs  = {"__might_sleep":"kernel/sched/core.c", "msleep":"kernel/time/timer.c", "usleep_range":"kernel/time/timer.c"}

added_funcs = funcs.copy()

res_nv =    ""
res_v =     "call(static inline void __might_sleep(const char *file, int line, int preempt_offset)) ||\n" \
            "\tcall(void msleep(unsigned int msecs)) ||\n" \
            "\tcall(void usleep_range(unsigned long min, unsigned long max)) ||\n"

callgraph_prefix = "Callgraph/callgraph" + path_in_build_base

for func, path in funcs.items():
    f = open(build_base_path + callgraph_prefix + path + ".json",)
    data = json.load(f)
    called_in = data[path_in_build_base + path][func]["called_in"]
    for i in called_in:
        for j in called_in[i]:
            if j in added_funcs:
                continue
            added_funcs[j] = i[41:]
            fd = open(build_base_path + "/Functions/functions/" + j + ".json", )
            fun = json.load(fd)
            l = fun[j][path_in_build_base + i[41:]]
            # FIXME: why can't it fins sognature?
            if (is_void(l["signature"].__str__())):
                # FIXME: Klever doesn't understand constructions in prototypes like int a[8u]
                if (l["signature"].__str__().find("[") == -1):
                    res_v += "\tcall("  + l["signature"].__str__()[:len(l["signature"].__str__()) - 1:] + ') || \n'
                added_funcs[j] = i[41:]
            else:
                # FIXME: Klever doesn't understand constructions in prototypes like int a[8u]
                if (l["signature"].__str__().find("[") == -1):
                    res_nv += "\tcall("  + l["signature"].__str__()[:len(l["signature"].__str__()) - 1:] + ') || \n'
                added_funcs[j] = i[41:]
            fd.close()
    f.close()


for k in range(depth - 1):
    funcs = added_funcs.copy()

    for func, path in funcs.items():
        f = open(build_base_path + callgraph_prefix + path + ".json",)
        data = json.load(f)
        
        if "called_in" not in data[path_in_build_base + path][func]:
            continue
        called_in = data[path_in_build_base + path][func]["called_in"]
        for i in called_in:
            for j in called_in[i]:
                if j in added_funcs:
                    continue
                added_funcs[j] = i[41:]
                fd = open(build_base_path + "/Functions/functions/" + j + ".json", )
                fun = json.load(fd)
                l = fun[j][path_in_build_base + i[41:]]
                if (not l["signature"]):
                    print(j)
                    continue
                # FIXME: why can't it fins sognature?
                if (is_void(l["signature"].__str__())):
                    # FIXME: Klever doesn't understand constructions in prototypes like int a[8u]
                    if (l["signature"].__str__().find("[") == -1):
                        res_v += "\tcall("  + l["signature"].__str__()[:len(l["signature"].__str__()) - 1:] + ') || \n'
                    added_funcs[j] = i[41:]
                else:
                    # FIXME: Klever doesn't understand constructions in prototypes like int a[8u]
                    if (l["signature"].__str__().find("[") == -1):
                        res_nv += "\tcall("  + l["signature"].__str__()[:len(l["signature"].__str__()) - 1:] + ') || \n'
                    added_funcs[j] = i[41:]
                fd.close()
        f.close()

res_nv = res_nv[:len(res_nv) - 4:]
res_v = res_v[:len(res_v) - 4:]
fr = open ("res_void.txt", "w")
fr.write(res_v)              
fr.close()
fr = open ("res_not_void.txt", "w")
fr.write(res_nv)     
fr.close()