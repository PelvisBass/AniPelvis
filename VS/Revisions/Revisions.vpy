import vapoursynth as vs
import havsfunc as haf
import fvsfunc as fvf
import mvsfunc as mvf
import vsTAAmbk as taa
import lvsfunc as lvf
import kagefunc as kgf
import vardefunc as vdf
core = vs.core
clip = core.ffms2.Source(source='D:\Misc\Encoding\Shows\Revisions\MKV\\revisionsBD-001.mkv')		#Video source
clip = core.resize.Bicubic(clip, format=vs.YUV444PS)
clip = lvf.scale.descale(clip, upscaler=lvf.scale.reupscale(), width=1280, height=720, kernel=lvf.kernels.Bicubic(), threshold=0.0, mask=lvf.scale.descale_detail_mask(), src_left=0.0, src_top=0.0, show_mask=False)
clip = fvf.Depth(clip, 16)

clip = haf.Deblock_QED(clip, quant1 = 26, quant2 = 28)	#deblocking

mask = lvf.denoise.detail_mask(clip, brz_a=2350, brz_b=2350)
filtered = core.knlm.KNLMeansCL(clip, a=2, h=0.6, d=3, device_type = 'gpu', device_id=0) #H is the strenght
filtered = haf.HQDeringmod(clip, mrad=2, msmooth=1, incedge=False, mthr=30, minp=1, nrmode=None, sharp=0, drrep=24, thr=12, elast=2.0, darkthr=None, planes=[0], show=False)	#dering
clip = core.std.MaskedMerge(filtered, clip, mask) #make sure order is correct
clip = haf.EdgeCleaner(clip, strength=8, rep=True, rmode=17, smode=1, hot=False) 		#Cleans around edges

clip = lvf.aa.nneedi3_clamp(clip, strength=2.75)
#clip = taa.TAAmbk(clip,aatype='Nnedi3', cycle=0, thin=0, dark=0.0, sharp=0, aarepair=0, stabilize=0)	#anti-alasing

debandmask = lvf.denoise.detail_mask(clip, brz_a=2000, brz_b=2000)
deband = core.neo_f3kdb.Deband(clip, y=18, cb=18, cr=18, grainy=10, grainc=5)		#debanding
clip = core.std.MaskedMerge(deband, clip, debandmask) #make sure order is correct
clip = kgf.adaptive_grain(clip, strength=0.15, static=True, luma_scaling=12, show_mask=False)

clip = core.resize.Bicubic(clip, format=vs.YUV420P16)
clip = fvf.Depth(clip, 10)
clip.set_output(0)