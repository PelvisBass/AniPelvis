import vapoursynth as vs
import havsfunc as haf
import fvsfunc as fvf
import lvsfunc as lvf
import kagefunc as kgf
core = vs.core
from vsutil import depth, join, plane
from functools import partial
#Debanding. I really have no clue how this works. Copied from Light
def debander(clip: vs.VideoNode, **deband_args) -> vs.VideoNode:
    return join([
        core.placebo.Deband(plane(clip, 0), grain=5, **deband_args),
        core.placebo.Deband(plane(clip, 1), grain=0, **deband_args),
        core.placebo.Deband(plane(clip, 2), grain=0, **deband_args)
    ])
#Args... I also do not really know anything about this but it helps with orginazing
deband_args = dict(iterations=2, threshold=4.5, radius=17)

clip = lvf.src(r"D:\Misc\ProjectYugi\Raws\Amzn\\YugiohSevensAMZNWEBRIP24.mkv")
clip = depth(clip, 32)
deblock = lvf.util.quick_resample(
    clip, partial(haf.Deblock_QED, quant1 = 25, quant2 = 27))
descaled = lvf.scale.descale(deblock, height=881)
descaled = depth(descaled, 16)

#Denoise and Deringing
mask = lvf.denoise.detail_mask(descaled, brz_a=1200, brz_b=1200)
filtered = core.knlm.KNLMeansCL(descaled, a=2, h=0.45, d=4, device_type = 'gpu', device_id=0) #H is strength
filtered = lvf.util.quick_resample(
    filtered, partial(haf.HQDeringmod, 
        mrad=2, msmooth=1, incedge=False, mthr=12, minp=1, nrmode=None, sharp=0, drrep=12, 
        thr=24, elast=2.0))
denoise = core.std.MaskedMerge(filtered, descaled, mask) #make sure order is correct

#Anti-Alasing
aa = lvf.util.quick_resample(
	denoise, partial(lvf.aa.nneedi3_clamp, strength=2)
)
#Edge cleaner, should work okay
edgeclean = lvf.util.quick_resample(
	aa, partial(haf.EdgeCleaner, strength=10, rmode=14)
)
debandmask = lvf.denoise.detail_mask(aa, brz_a=650, brz_b=650)
deband = debander(aa, **deband_args)
clip = core.std.MaskedMerge(deband, aa, debandmask) #make sure order is correct
clip = kgf.adaptive_grain(clip, strength=0.1, static=True, luma_scaling=4, show_mask=False)
clip = fvf.Depth(clip, 10)
clip.set_output(0)