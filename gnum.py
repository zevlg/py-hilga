#!/usr/bin/env python
# coding: utf-8

import sys

def usage():
    print "usage: %s N N1 [N2 [N3 ..]]" % sys.argv[0]
    sys.exit(0)

def expressions(num1, num2):
    for op in '-', '+', '/', '*':
        yield num1 + op + num2
        if num2[-1] != ')':
            yield '(' + num1 + op + num2 + ')'

def gexp(n, nums, ret):
    if len(nums) == 1:
        try:
            if eval(nums[0]) == n:
                ret.append(nums[0])
        except ZeroDivisionError:
            pass
        return
        # NOT REACHED

    for i1, nm1 in enumerate(nums):
        nums2 = nums[:i1] + nums[i1+1:]
        for i2, nm2 in enumerate(nums2):
            nums3 = nums2[:i2] + nums2[i2+1:]
            for exp in expressions(nm1, nm2):
                gexp(n, [exp] + nums3, ret)

    return ret

def main():
    if len(sys.argv) < 3:
        usage()

    n = int(sys.argv[1])
    nums = sys.argv[2:]

    for r in gexp(n, nums, []):
        print r, "=", n

if __name__ == '__main__':
    main()
