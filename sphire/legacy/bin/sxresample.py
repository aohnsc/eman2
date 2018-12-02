#!/usr/bin/env python
from __future__ import print_function
#
# Author: Pawel A.Penczek and Edward H. Egelman 05/27/2009 (Pawel.A.Penczek@uth.tmc.edu)
# Copyright (c) 2000-2006 The University of Texas - Houston Medical School
# Copyright (c) 2008-Forever The University of Virginia
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#

import EMAN2_cppwrap
import global_def
import mpi
import numpy
import numpy.random
import optparse
import os
import random
import sys
import time
import utilities
pass#IMPORTIMPORTIMPORT import EMAN2
pass#IMPORTIMPORTIMPORT import EMAN2_cppwrap
pass#IMPORTIMPORTIMPORT import global_def
pass#IMPORTIMPORTIMPORT import mpi
pass#IMPORTIMPORTIMPORT import numpy
pass#IMPORTIMPORTIMPORT import numpy.random
pass#IMPORTIMPORTIMPORT import optparse
pass#IMPORTIMPORTIMPORT import os
pass#IMPORTIMPORTIMPORT import random
pass#IMPORTIMPORTIMPORT import sparx
pass#IMPORTIMPORTIMPORT import sys
pass#IMPORTIMPORTIMPORT import time
pass#IMPORTIMPORTIMPORT import utilities
from builtins import range
pass#IMPORTIMPORTIMPORT import global_def
pass#IMPORTIMPORTIMPORT from   global_def import *

pass#IMPORTIMPORTIMPORT from   EMAN2 import *
pass#IMPORTIMPORTIMPORT from   sparx import *
pass#IMPORTIMPORTIMPORT from   numpy import *
pass#IMPORTIMPORTIMPORT from   time import time
pass#IMPORTIMPORTIMPORT from   optparse import OptionParser
pass#IMPORTIMPORTIMPORT import numpy.random

def resample_insert( bufprefix, fftvols, wgtvols, mults, CTF, npad, info=None):
	pass#IMPORTIMPORTIMPORT from EMAN2 import  newfile_store
	ostore = EMAN2_cppwrap.newfile_store( bufprefix, npad, CTF )
	blocksize = 250
	nvol = len(fftvols)
	nprj = len(mults[0])
	nblock = (nprj-1)/blocksize + 1

	overall_start = time.time()

	for iblock in range(nblock):
		if iblock==nblock - 1:
			pbeg = iblock*blocksize
			pend = nprj
		else:
			pbeg = iblock*blocksize
			pend = pbeg + blocksize

		start_time = time.time()
		ostore.read( pend - pbeg )
		if not(info is None):
			t = time.time()
			info.write("        block %d read.   \t time: %10.3f %10.3f\n" % (iblock, t-start_time, t-overall_start) )
			info.flush()

		start_time = time.time()
		for ivol in range(nvol):
			ostore.add_tovol( fftvols[ivol], wgtvols[ivol], mults[ivol], pbeg, pend )
		if not(info is None):
			t = time.time()
			info.write("        block %d inserted.\t time: %10.3f %10.3f\n" % (iblock, t-start_time, t-overall_start) )
			info.flush()

	if not(info is None):
		info.write("    Projection inserted.\t time: %10.3f\n" % (time.time() - overall_start) )
		info.flush()

def resample_finish( rectors, fftvols, wgtvols, volfile, niter, nprj, info=None ):
	pass#IMPORTIMPORTIMPORT from time import time
	overall_start = time.time()
	nvol = len(fftvols)
	for ivol in range(nvol):
		start_time = time.time()
		iwrite = nvol*niter + ivol

		dummy = rectors[ivol].finish(True)
		# Here add multiplication as per Kimmel-Penczek formula
		EMAN2_cppwrap.Util.mul_scalar( fftvols[ivol], float(nprj) )          # ??????????
		fftvols[ivol].write_image( volfile, iwrite )
		if not(info is None):
			t = time.time()
			info.write( "        vol %d reconstred.\t time: %10.3f %10.3f\n" % (ivol, t-start_time, t-overall_start) )
			info.flush()

	if not(info is None):
		info.write( "    Volume finished.\t time: %10.3f\n" % (time.time() - overall_start) )

def resample_prepare( prjfile, nvol, snr, CTF, npad ):
	pass#IMPORTIMPORTIMPORT from utilities import get_im
	nx = utilities.get_im( prjfile, 0 ).get_xsize()
	fftvols = [None]*nvol
	wgtvols = [None]*nvol
	rectors = [None]*nvol
	for i in range(nvol):
		fftvols[i] = EMAN2_cppwrap.EMData()
		wgtvols[i] = EMAN2_cppwrap.EMData()
		if CTF:
			params = {"size":nx, "npad":npad, "snr":snr, "weight":wgtvols[i], "fftvol":fftvols[i]}
			rectors[i] = EMAN2_cppwrap.Reconstructors.get( "nn4_ctf", params )
		else:
			params = {"size":nx, "npad":npad, "snr":snr, "weight":wgtvols[i], "fftvol":fftvols[i]}
			rectors[i] = EMAN2_cppwrap.Reconstructors.get( "nn4", params )

		rectors[i].setup()

	return rectors, fftvols, wgtvols

def resample( prjfile, outdir, bufprefix, nbufvol, nvol, seedbase,\
		delta, d, snr, CTF, npad,\
		MPI, myid, ncpu, verbose = 0 ):
	pass#IMPORTIMPORTIMPORT from   utilities import even_angles
	pass#IMPORTIMPORTIMPORT from   random import seed, jumpahead, shuffle
	pass#IMPORTIMPORTIMPORT import os
	pass#IMPORTIMPORTIMPORT from   sys import exit

	nprj = EMAN2_cppwrap.EMUtil.get_image_count( prjfile )

	if MPI:
		pass#IMPORTIMPORTIMPORT from mpi import mpi_barrier, MPI_COMM_WORLD

		if myid == 0:
			if os.path.exists(outdir):  nx = 1
			else:  nx = 0
		else:  nx = 0
		ny = utilities.bcast_number_to_all(nx, source_node = 0)
		if ny == 1:  global_def.ERROR('Output directory exists, please change the name and restart the program', "resample", 1,myid)
		mpi.mpi_barrier(mpi.MPI_COMM_WORLD)

		if myid == 0:
			os.mkdir(outdir)
		mpi.mpi_barrier(mpi.MPI_COMM_WORLD)
	else:
		if os.path.exists(outdir):
			global_def.ERROR('Output directory exists, please change the name and restart the program', "resample", 1,0)
		os.mkdir(outdir)

	if(verbose == 1):  finfo=open( os.path.join(outdir, "progress%04d.txt" % myid), "w" )
	else:              finfo = None
	#print  " before evenangles",myid
	pass#IMPORTIMPORTIMPORT from utilities import getvec
	pass#IMPORTIMPORTIMPORT from numpy import array, reshape
	refa = utilities.even_angles(delta)
	nrefa = len(refa)
	refnormal = numpy.zeros((nrefa,3),'float32')

	tetref = [0.0]*nrefa
	for i in range(nrefa):
		tr = utilities.getvec( refa[i][0], refa[i][1] )
		for j in range(3):  refnormal[i][j] = tr[j]
		tetref[i] = refa[i][1]
	del refa
	vct = numpy.array([0.0]*(3*nprj),'float32')
	if myid == 0:
		print(" will read ",myid)
		tr = EMAN2_cppwrap.EMUtil.get_all_attributes(prjfile,'xform.projection')
		tetprj = [0.0]*nprj
		for i in range(nprj):
			temp = tr[i].get_params("spider")
			tetprj[i] = temp["theta"]
			if(tetprj[i] > 90.0): tetprj[i]  = 180.0 - tetprj[i] 
			vct[3*i+0] = tr[i].at(2,0)
			vct[3*i+1] = tr[i].at(2,1)
			vct[3*i+2] = tr[i].at(2,2)
		del tr
	else:
		tetprj = [0.0]*nprj
	#print "  READ ",myid
	if  MPI:
		#print " will bcast",myid
		pass#IMPORTIMPORTIMPORT from mpi import mpi_bcast, MPI_FLOAT, MPI_COMM_WORLD
		vct = mpi.mpi_bcast(vct,len(vct),mpi.MPI_FLOAT,0,mpi.MPI_COMM_WORLD)
		pass#IMPORTIMPORTIMPORT from utilities import  bcast_list_to_all
		tetprj = utilities.bcast_list_to_all(tetprj, myid, 0)
	#print  "  reshape  ",myid
	vct = numpy.reshape(vct,(nprj,3))
	assignments = [[] for i in range(nrefa)]
	dspn = 1.25*delta
	for k in range(nprj):
		best_s = -1.0
		best_i = -1
		for i in range( nrefa ):
			if(abs(tetprj[k] - tetref[i]) <= dspn):
				s = abs(refnormal[i][0]*vct[k][0] + refnormal[i][1]*vct[k][1] + refnormal[i][2]*vct[k][2])
				if s > best_s:
					best_s = s
					best_i = i
			assignments[best_i].append(k)
	am = len(assignments[0])
	mufur = 1.0/am
	for i in range(1,len(assignments)):
		ti = len(assignments[i])
		am = min(am, ti)
		if(ti>0):  mufur += 1.0/ti

	del tetprj,tetref

	dp = 1.0 - d  # keep that many in each direction
	keep = int(am*dp +0.5)
	mufur = keep*nrefa/(1.0 - mufur*keep/float(nrefa))
	if myid == 0:
		print(" Number of projections ",nprj,".  Number of reference directions ",nrefa,",  multiplicative factor for the variance ",mufur)
		print(" Minimum number of assignments ",am,"  Number of projections used per stratum ", keep," Number of projections in resampled structure ",int(am*dp +0.5)*nrefa)
		if am <2 or am == keep:
			print("incorrect settings")
			exit()  #                                         FIX

	if(seedbase < 1):
		random.seed()
		random.jumpahead(17*myid+123)
	else:
		random.seed(seedbase)
		random.jumpahead(17*myid+123)

	volfile = os.path.join(outdir, "bsvol%04d.hdf" % myid)
	pass#IMPORTIMPORTIMPORT from random import randint
	niter = nvol/ncpu/nbufvol
	for kiter in range(niter):
		if(verbose == 1):
			finfo.write( "Iteration %d: \n" % kiter )
			finfo.flush()

		iter_start = time.time()
		#  the following has to be converted to resample  mults=1 means take given projection., mults=0 means omit

		mults = [ [0]*nprj for i in range(nbufvol) ]
		for i in range(nbufvol):
			for l in range(nrefa):
				mass = assignments[l][:]
				numpy.random.shuffle(mass)
				mass = mass[:keep]
				mass.sort()
				#print  l, "  *  ",mass
				for k in range(keep):
					mults[i][mass[k]] = 1
			'''
			lout = []
			for l in xrange(len(mults[i])):
				if mults[i][l] == 1:  lout.append(l)
			write_text_file(lout, os.path.join(outdir, "list%04d_%03d.txt" %(i, myid)))
			del lout
			'''

		del mass

		rectors, fftvols, wgtvols = resample_prepare( prjfile, nbufvol, snr, CTF, npad )
		resample_insert( bufprefix, fftvols, wgtvols, mults, CTF, npad, finfo )
		del mults
		resample_finish( rectors, fftvols, wgtvols, volfile, kiter, nprj, finfo )
		rectors = None
		fftvols = None
		wgtvols = None
		if(verbose == 1):
			finfo.write( "time for iteration: %10.3f\n" % (time.time() - iter_start) )
			finfo.flush()

def main():

	pass#IMPORTIMPORTIMPORT import sys

	arglist = []
	for arg in sys.argv:
		arglist.append( arg )

	progname = os.path.basename(arglist[0])
	usage = progname + " prjstack outdir bufprefix --delta --d --nvol --nbufvol --seedbase --snr --npad --CTF --MPI --verbose"
	parser = optparse.OptionParser(usage,version=global_def.SPARXVERSION)
	parser.add_option("--nvol",     type="int",                         help="number of resample volumes to be generated")
	parser.add_option("--nbufvol",  type="int",          default=1,     help="number of fftvols in the memory")
	parser.add_option("--delta",    type="float",        default=10.0,  help="angular step for cones")
	parser.add_option("--d",        type="float",        default=0.1,   help="fraction of projections to leave out")
	parser.add_option("--CTF",      action="store_true", default=False, help="use CTF")
	parser.add_option("--snr",      type="float",        default=1.0,   help="Signal-to-Noise Ratio")
	parser.add_option("--npad",     type="int",          default=2,     help="times of padding")
	parser.add_option("--seedbase", type="int",          default=-1,    help="random seed base")
	parser.add_option("--MPI",      action="store_true", default=False, help="use MPI")
	parser.add_option("--verbose",  type="int",          default=0,     help="verbose level: 0 no, 1 yes")

	(options, args) = parser.parse_args( arglist[1:] )

	if( len(args) !=1 and len(args) != 3):
		print("usage: " + usage)
		return None

	prjfile = args[0]

	if options.MPI:
		pass#IMPORTIMPORTIMPORT from mpi import mpi_barrier, mpi_comm_rank, mpi_comm_size, mpi_comm_split, MPI_COMM_WORLD
		pass#IMPORTIMPORTIMPORT from mpi import mpi_init
		sys.argv = mpi.mpi_init( len(sys.argv), sys.argv )
		myid = mpi.mpi_comm_rank( mpi.MPI_COMM_WORLD )
		ncpu = mpi.mpi_comm_size( mpi.MPI_COMM_WORLD )
	else:
		myid = 0
		ncpu = 1

	if global_def.CACHE_DISABLE:
		pass#IMPORTIMPORTIMPORT from utilities import disable_bdb_cache
		utilities.disable_bdb_cache()

	outdir = args[1]
	bufprefix = args[2]
	resample( prjfile, outdir, bufprefix, options.nbufvol, options.nvol, options.seedbase,\
	           options.delta, options.d, options.snr, options.CTF, options.npad,\
		   options.MPI, myid, ncpu, options.verbose )
	if options.MPI:
		pass#IMPORTIMPORTIMPORT from mpi import mpi_finalize
		mpi.mpi_finalize()


if __name__ == "__main__":
	main()