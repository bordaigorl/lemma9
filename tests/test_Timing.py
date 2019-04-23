from Timing import *
from collections import OrderedDict

prefix = "../benchmarks/"


def test_get_benchmark_times():
    # Change here to adjust number of samples
    num_samples = 1
    pairs = OrderedDict({
            "ARPC":
                ("Andrew-Secure-RPC/Andrew-RPC-1-widen.txt",
                 "Andrew-Secure-RPC/Andrew-RPC-2-invariant.txt", 
                 "secret", "F"),
            "KSL":
                ("Kehne-Schoenwaelder-Landendoerfer/KSL-1-without-reauth-widen.txt",
                 "Kehne-Schoenwaelder-Landendoerfer/KSL-2-without-reauth-invariant.txt",
                 "secret", "F"),
            "KSLR":
                ("Kehne-Schoenwaelder-Landendoerfer/KSL-3-continuous-reauth-widen.txt",
                 "Kehne-Schoenwaelder-Landendoerfer/KSL-4-continuous-reauth-invariant.txt",
                 "secret", "F"),
            "NHS":
                ("Needham-Schroeder/Needham-Schroeder-1-widen.txt",
                 "Needham-Schroeder/Needham-Schroeder-2-invariant.txt",
                 "not modelled", "F"),
            "NHSL":
                (("Needham-Schroeder-Lowe/Needham-Schroeder-Lowe-A-Non-Leaky-widen.txt",
                  "Needham-Schroeder-Lowe/Needham-Schroeder-Lowe-B-Leaky-widen.txt"),
                 "Needham-Schroeder-Lowe/Needham-Schroeder-Lowe-A+B-merged-invariant.txt",
                 "secret", "I"),
            "OR":
                ("Otway-Rees/Otway-Rees-CSF-1-widen.txt",
                 "Otway-Rees/Otway-Rees-CSF-2-invariant.txt",
                 "not modelled", "F"),
            "ORl":
                ("Otway-Rees/Otway-Rees-Leaky-1-widen.txt",
                 "Otway-Rees/Otway-Rees-Leaky-2-invariant.txt",
                 "not secret", "F"),
            "ORs":
                ("Otway-Rees/Otway-Rees-Secret-1-widen.txt",
                 "Otway-Rees/Otway-Rees-Secret-2-invariant.txt",
                 "secret", "F"),
            "Ex.9":
                ("Running-Example-Paper/Running-Example-1-widen.txt",
                 "Running-Example-Paper/Running-Example-3-invariant.txt",
                 "secret", "F"),
            "YAH":
                ("Yahalom/Yahalom-CSF-1-widen.txt",
                 "Yahalom/Yahalom-CSF-2-invariant.txt", "not modelled", "F"),
            "YAHs1":
                ("Yahalom/Yahalom-Secret-ny-not-leaked-1-widen.txt",
                 "Yahalom/Yahalom-Secret-ny-not-leaked-2-invariant.txt", "secret", "F"),
            "YAHs2":
                ("Yahalom/Yahalom-Secret-size-key-1-widen.txt",
                 "Yahalom/Yahalom-Secret-size-key-2-invariant.txt", "secret", "F")
    })
    results = "\nName \t\tInfer \t\tC \t\tS \n"
    for (name, (fws, fi, model, how)) in pairs.iteritems():
        results += name + "\t\t"
        result_w = 0
        if isinstance(fws, tuple):
            for fw in fws:
                result_w += time_widening_sampling(prefix + fw, num_samples)
        else:
            result_w = time_widening_sampling(prefix + fws, num_samples)
        results += "%.1fs" % result_w + "\t" + how + "\t"
        result_i = time_inv_check_sampling(prefix + fi, num_samples)
        results += "%.1fs" % result_i + " \t" + model + "\n"
    print results
