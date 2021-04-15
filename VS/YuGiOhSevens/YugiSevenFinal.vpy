import debandshit as dbs
import havsfunc as haf
import kagefunc as kgf
import lvsfunc as lvf
import mvsfunc as mvf
from finedehalo import fine_dehalo
from functools import partial
import vardefunc as vdf 
import vapoursynth as vs
from vsutil import depth, iterate, join, plane
core = vs.core

src = lvf.src('D:\Misc\ProjectYugi\Raws\MakeMKV\\NCOP1V2.mkv')
src = depth(src, 32)

descaled = lvf.scale.descale(src, upscaler=None, height=881, kernel=lvf.kernels.Spline36())
luma_upscale = vdf.fsrcnnx_upscale(descaled, 1920, 1080, shader_file="C:\CTP\Vapoursynth\shaders\FSRCNNX_x2_56-16-4-1.glsl") \
    .resize.Spline36(1920, 1080)
chroma_upscale = core.resize.Bicubic(src, luma_upscale.width, luma_upscale.height)
scaled = join([plane(luma_upscale, 0), plane(chroma_upscale, 1), plane(chroma_upscale, 2)])
scaled = depth(scaled, 16)

noisemask = lvf.mask.detail_mask(scaled, brz_a=960, brz_b=960)
debandmask = lvf.mask.detail_mask(scaled, sigma=0.35, brz_a=925, brz_b=925)

denoise = core.knlm.KNLMeansCL(scaled, h=3.2, d=2) #H is strength
denoise = core.std.MaskedMerge(denoise, scaled, noisemask)

edgec = haf.EdgeCleaner(denoise, strength=4, rmode=13, hot=True)
aa = lvf.aa.nneedi3_clamp(edgec, strength=1.3)
dehalo = fine_dehalo(aa, rx=2.6, ry=2.4, thmi=80, thma=132, darkstr=0.1, brightstr=0.85)

##TEMP Adjust as needed
deband = core.neo_f3kdb.Deband(aa, range=15, y=38, cb=32, cr=32, grainy=22, grainc=0, sample_mode=4)
deband = core.std.MaskedMerge(deband, aa, debandmask)

grain = kgf.adaptive_grain(deband, 0.15, luma_scaling=4)

out = grain
final = depth(out, 10)
final.set_output()
