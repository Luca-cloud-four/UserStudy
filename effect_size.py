sd, r = 1.2, 0.75
diff = 0.2
sd_diff = sd * (2 * (1 - r)) ** 0.5   # SD of before-after differences
d_av = diff / sd                      # comparable to between-group d
d_z  = diff / sd_diff                 # for paired (within-subject) tests