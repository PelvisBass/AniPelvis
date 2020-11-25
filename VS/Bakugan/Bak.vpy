import vapoursynth as vs
import havsfunc as haf
import fvsfunc as fvf
import mvsfunc as mvf
import vsTAAmbk as taa
import lvsfunc as lvf
import kagefunc as kgf
import nnedi3_rpow2 as ndi
core = vs.core
clip = core.ffms2.Source(source='D:\Misc\Encoding\Shows\Bakugan\Makemkv\DVD1\\title_t01.mkv')		#Video source
clip = clip[1899:2000]	#start and end frames for when I want to cu
clip = haf.QTGMC(clip, TFF=True,SourceMatch=3, Lossless=2, TR0=1, TR1=2, TR2=3, FPSDivisor=2) #Deinterlacing
clip = core.vivtc.VDecimate(clip)
clip = ndi.nnedi3_rpow2(clip, width=1024, height=576)
clip = core.resize.Bicubic(clip, format=vs.YUV444PS)
clip = fvf.Depth(clip, 16)
clip = haf.Deblock_QED(clip, quant1 = 26, quant2 = 28)	#deblocking

mask = lvf.denoise.detail_mask(clip, brz_a=4350, brz_b=4350)
filtered = mvf.BM3D(clip, profile1="fast",radius1=1, sigma=[2.5, 2.7, 2.5]) 		#Denoising (Keep around .5 - 3)
filtered = haf.HQDeringmod(clip, mrad=2, msmooth=1, incedge=False, mthr=45, minp=1, nrmode=None, sharp=1, drrep=24, thr=12, elast=2.0, darkthr=None, planes=[0], show=False)	#dering
clip = core.std.MaskedMerge(filtered, clip, mask) #make sure order is correct
clip = haf.EdgeCleaner(clip, strength=10, rep=True, rmode=17, smode=1, hot=True) 		#Cleans around edges

clip = taa.TAAmbk(clip,aatype='Nnedi3', cycle=0, thin=0, dark=0.00, sharp=0, aarepair=0, stabilize=0)	#anti-alasing
clip = core.neo_f3kdb.Deband(clip, y=32, cb=32, cr=32, grainy=15, grainc=10)		#debanding
clip = kgf.adaptive_grain(clip, strength=0.2, static=True, luma_scaling=12, show_mask=False)

#clip = core.resize.Bicubic(clip, format=vs.YUV444P16)	#resizing
clip = fvf.Depth(clip, 10)
clip.set_output()