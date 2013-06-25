# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
import os

def customise(process):
   
  inputProcess="HLT"  # some automagic check possible?

  process._Process__name="EmbeddedRECO"
  process.TFileService = cms.Service("TFileService",  fileName = cms.string("histo_embedded.root")          )

  try:
	  outputModule = process.output
  except:
    pass
  try:
	  outputModule = getattr(process,str(getattr(process,list(process.endpaths)[-1])))
  except:
    pass

  print "Changing eventcontent to RAW+AODSIM + misc. "
  outputModule.outputCommands = cms.untracked.vstring("drop *")
  outputModule.outputCommands.extend(process.RAWEventContent.outputCommands )
  outputModule.outputCommands.extend(process.AODSIMEventContent.outputCommands )

  keepMC = cms.untracked.vstring("keep *_*_zMusExtracted_*",
                                 "keep *_*_zmmCands_*",
                                 "keep *_removedInputMuons_*_*",
                                 "keep *_generator_*_*",
                                 "keep *_PhotonIDProd_*_*",
                                 "keep *_photons_*_*",
                                 "keep *_photonCore_*_*",
                                 "keep *_genParticles_*_*",
                                 "keep *_particleFlow_*_*",
                                 "keep *_generator_*_*",
                                 "keep *_tmfTracks_*_EmbeddedRECO",
                                 "keep *_offlinePrimaryVertices_*_EmbeddedRECO",
                                 "keep *_offlinePrimaryVerticesWithBS_*_EmbeddedRECO",
                                 "keep *_PhotonIDProd_*_*",
                                 "keep *_photons_*_*",
                                 "keep *_photonCore_*_*",
                                 "keep *_genParticles_*_*",
                                 "keep *_particleFlow_*_*",
  )
  outputModule.outputCommands.extend(keepMC)

  # getRid of second "drop *"
  index = 0
  for item in outputModule.outputCommands[:]:
    if item == "drop *" and index != 0:
      #print index," ",outputModule.outputCommands[index]
      del outputModule.outputCommands[index]
      index -= 1
    index += 1  


  hltProcessName = "HLT"	#"REDIGI38X"
  # the following block can be used for more efficient processing by replacing the HLT variable below automatically
  try:
    hltProcessName = __HLT__
  except:
    pass
	
  try:
    process.dimuonsHLTFilter.TriggerResultsTag.processName = hltProcessName
    process.goodZToMuMuAtLeast1HLT.TrigTag.processName = hltProcessName
    process.goodZToMuMuAtLeast1HLT.triggerEvent.processName = hltProcessName
    process.hltTrigReport,HLTriggerResults.processName = hltProcessName
  except:
    pass

  process.VtxSmeared = cms.EDProducer("FlatEvtVtxGenerator", 
    MaxZ = cms.double(0.0),
    MaxX = cms.double(0.0),
    MaxY = cms.double(0.0),
    MinX = cms.double(0.0),
    MinY = cms.double(0.0),
    MinZ = cms.double(0.0),
    TimeOffset = cms.double(0.0),
    src = cms.InputTag("generator")
  )

  import FWCore.ParameterSet.VarParsing as VarParsing
  options = VarParsing.VarParsing ('analysis')
  options.register ('mdtau',
                    0, # default value
                    VarParsing.VarParsing.multiplicity.singleton,
                    VarParsing.VarParsing.varType.int,         
                    "mdtau value for tauola")

  options.register ('transformationMode',
                    1, #default value
                    VarParsing.VarParsing.multiplicity.singleton,
                    VarParsing.VarParsing.varType.int,
                    "transformation mode. 0=mumu->mumu, 1=mumu->tautau")

  options.register ('minVisibleTransverseMomentum',
                    "", #default value
                    VarParsing.VarParsing.multiplicity.singleton,
                    VarParsing.VarParsing.varType.string,
                    "generator level cut on visible transverse momentum (typeN:pT,[...];[...])")

  options.register ('useJson',
                    0, # default value, false
                    VarParsing.VarParsing.multiplicity.singleton,
                    VarParsing.VarParsing.varType.int,         
                    "should I enable json usage?")

  options.register ('overrideBeamSpot',
                    0, # default value, false
                    VarParsing.VarParsing.multiplicity.singleton,
                    VarParsing.VarParsing.varType.int,         
                    "should I override beamspot in globaltag?")

#  options.register ('primaryProcess',
#                    'RECO', # default value
#                     VarParsing.VarParsing.multiplicity.singleton,
#                     VarParsing.VarParsing.varType.string,
#                     "original processName")



  setFromCL = False
  if not hasattr(process,"doNotParse"):
    import sys
    if hasattr(sys, "argv") == True:
      if not sys.argv[0].endswith('cmsDriver.py'):
        options.parseArguments()
        setFromCL = True
  else :
    print "CL parsing disabled!"

  
  if setFromCL:
    print "Setting mdtau to ", options.mdtau
    process.generator.ZTauTau.TauolaOptions.InputCards.mdtau = options.mdtau 
    process.newSource.ZTauTau.TauolaOptions.InputCards.mdtau = options.mdtau
    process.generator.ParticleGun.ExternalDecays.Tauola.InputCards.mdtau = options.mdtau 
    process.newSource.ParticleGun.ExternalDecays.Tauola.InputCards.mdtau = options.mdtau 

    print "Setting minVisibleTransverseMomentum to ", options.minVisibleTransverseMomentum
    process.newSource.ZTauTau.minVisibleTransverseMomentum = cms.untracked.string(options.minVisibleTransverseMomentum)
    process.generator.ZTauTau.minVisibleTransverseMomentum = cms.untracked.string(options.minVisibleTransverseMomentum)

    print "Setting transformationMode to ", options.transformationMode
    process.generator.ZTauTau.transformationMode = cms.untracked.int32(options.transformationMode)
    process.newSource.ZTauTau.transformationMode = cms.untracked.int32(options.transformationMode)

  if setFromCL and options.overrideBeamSpot != 0  :
    print "options.overrideBeamSpot", options.overrideBeamSpot
    # bs = cms.string("BeamSpotObjects_2009_LumiBased_SigmaZ_v26_offline") # 52x data PR gt
    bs = cms.string("BeamSpotObjects_2009_LumiBased_SigmaZ_v21_offline") # 42x data PR gt
    # bs = cms.string("BeamSpotObjects_2009_LumiBased_SigmaZ_v18_offline") # 41x data PR gt
    # bs = cms.string("BeamSpotObjects_2009_LumiBased_v17_offline") # 38x data gt
    #bs = cms.string("BeamSpotObjects_2009_v14_offline") # 36x data gt
    #  tag = cms.string("Early10TeVCollision_3p8cm_31X_v1_mc_START"), # 35 default
    #  tag = cms.string("Realistic900GeVCollisions_10cm_STARTUP_v1_mc"), # 36 default
    process.GlobalTag.toGet = cms.VPSet(
      cms.PSet(record = cms.string("BeamSpotObjectsRcd"),
           tag = bs,
           connect = cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_BEAMSPOT")
      )
    )
    print "BeamSpot in globaltag set to ", bs 
  else:
    print "BeamSpot in globaltag not changed"

  if setFromCL and options.useJson !=  0:
    print "Enabling json usage"
    import PhysicsTools.PythonAnalysis.LumiList as LumiList
    import FWCore.ParameterSet.Types as CfgTypes
    myLumis = LumiList.LumiList(filename = 'my.json').getCMSSWString().split(',')
    process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
    process.source.lumisToProcess.extend(myLumis)



  
  process.generalTracksORG = process.generalTracks.clone()

  process.generalTracks = cms.EDProducer("RecoTracksMixer",
      trackCol1 = cms.InputTag("generalTracksORG","","EmbeddedRECO"),
      trackCol2 = cms.InputTag("removedInputMuons","tracks")
  )  

  for p in process.paths:
    pth = getattr(process,p)
    if "generalTracks" in pth.moduleNames():
      pth.replace(process.generalTracks, process.generalTracksORG*process.generalTracks)

  # We can try mixing seeds or keep std::vector<Trajectory> from Zmumu event and
  # try mixing it. 
  # note - later approach may have no sense. Different geometries...
  process.trackerDrivenElectronSeedsORG = process.trackerDrivenElectronSeeds.clone()
  process.trackerDrivenElectronSeedsORG.TkColList = cms.VInputTag(cms.InputTag("generalTracksORG"))

  process.trackerDrivenElectronSeeds = cms.EDProducer("ElectronSeedTrackRefUpdater",
    PreIdLabel = process.trackerDrivenElectronSeedsORG.PreIdLabel,
    PreGsfLabel = process.trackerDrivenElectronSeedsORG.PreGsfLabel,
    targetTracks = cms.InputTag("generalTracks"),
    inSeeds = cms.InputTag("trackerDrivenElectronSeedsORG", process.trackerDrivenElectronSeedsORG.PreGsfLabel.value()),
    inPreId = cms.InputTag("trackerDrivenElectronSeedsORG", process.trackerDrivenElectronSeedsORG.PreIdLabel.value()),
  )

  for p in process.paths:
    pth = getattr(process,p)
    if "trackerDrivenElectronSeeds" in pth.moduleNames():
        pth.replace(process.trackerDrivenElectronSeeds, process.trackerDrivenElectronSeedsORG*process.trackerDrivenElectronSeeds)


  # hack photonCore:
  process.trackerDrivenElectronSeedsMerged = cms.EDProducer("ElectronSeedTrackRefUpdaterAndMerger",
   PreIdLabel = process.trackerDrivenElectronSeedsORG.PreIdLabel,
   PreGsfLabel = process.trackerDrivenElectronSeedsORG.PreGsfLabel,
   targetTracks = cms.InputTag("generalTracks"),
   inSeeds1 = cms.InputTag("trackerDrivenElectronSeedsORG", process.trackerDrivenElectronSeeds.PreGsfLabel.value()),
   inPreId1 = cms.InputTag("trackerDrivenElectronSeedsORG", process.trackerDrivenElectronSeeds.PreIdLabel.value()),
   inSeeds2 = cms.InputTag("trackerDrivenElectronSeeds", process.trackerDrivenElectronSeeds.PreGsfLabel.value()),
   inPreId2 = cms.InputTag("trackerDrivenElectronSeeds", process.trackerDrivenElectronSeeds.PreIdLabel.value())
  )

  process.electronMergedSeedsPhotonCoreHack = cms.EDProducer("ElectronSeedMerger",
    EcalBasedSeeds = cms.InputTag("ecalDrivenElectronSeeds"),
    TkBasedSeeds = cms.InputTag("trackerDrivenElectronSeedsMerged","SeedsForGsf")
  )

  process.photonCore.pixelSeedProducer = cms.string('electronMergedSeedsPhotonCoreHack')


  for p in process.paths:
    pth = getattr(process,p)
    if "photonCore" in pth.moduleNames():
        pth.replace(process.photonCore, 
                    process.trackerDrivenElectronSeedsMerged * process.electronMergedSeedsPhotonCoreHack *process.photonCore)




  # mix gsfTracks
  process.electronGsfTracksORG = process.electronGsfTracks.clone()
  process.electronGsfTracks = cms.EDProducer("GsfTrackMixer", 
      col1 = cms.InputTag("electronGsfTracksORG","","EmbeddedRECO"),
      col2= cms.InputTag("electronGsfTracks","", inputProcess),
  )

  # TODO: in 42x conversions seem not be used anywhere during reco. What about ana?
  # what about 52X?
  process.gsfConversionTrackProducer.TrackProducer = cms.string('electronGsfTracksORG')

  for p in process.paths:
    pth = getattr(process,p)
    if "electronGsfTracks" in pth.moduleNames():
        pth.replace(process.electronGsfTracks, process.electronGsfTracksORG*process.electronGsfTracks)





  '''
  process.electronMergedSeedsORG = process.electronMergedSeeds.clone()
  process.electronMergedSeeds = cms.EDProducer("ElectronSeedsMixer",
      col1 = cms.InputTag("electronMergedSeeds","", inputProcess),
      col2 = cms.InputTag("electronMergedSeedsORG","","EmbeddedRECO")
  )
  for p in process.paths:
    pth = getattr(process,p)
    if "electronMergedSeeds" in pth.moduleNames():
      pth.replace(process.electronMergedSeeds, process.electronMergedSeedsORG*process.electronMergedSeeds)
  '''

  process.generalConversionTrackProducer.TrackProducer = cms.string('generalTracksORG')


  process.gsfElectronsORG = process.gsfElectrons.clone()
  process.gsfElectrons = cms.EDProducer("GSFElectronsMixer",
      col1 = cms.InputTag("gsfElectronsORG"),
      col2 = cms.InputTag("gsfElectrons","",inputProcess),
  )
  for p in process.paths:
    pth = getattr(process,p)
    if "gsfElectrons" in pth.moduleNames():
      pth.replace(process.gsfElectrons, process.gsfElectronsORG*process.gsfElectrons)




  for p in process.paths:
    pth = getattr(process,p)
    #print dir(pth)
    #sys.exit(0)
    for mod in pth.moduleNames():
      if mod.find("dedx") != -1:
        print "Removing", mod
        module=getattr(process,mod)
        pth.remove(module)


 
  clConfig = cms.PSet (
             depsPlus = cms.InputTag("anaDeposits", "plus" ),
             depsMinus = cms.InputTag("anaDeposits", "minus" )
  ) 



  process.castorrecoORG = process.castorreco.clone()
  process.castorreco = cms.EDProducer("CastorRHMixer",
       cleaningAlgo = cms.string("CaloCleanerAllCrossed"),
       cleaningConfig = clConfig,
       todo = cms.VPSet(cms.PSet ( colZmumu = cms.InputTag("castorreco","", inputProcess  ), colTauTau = cms.InputTag("castorrecoORG" )  ))
  )

  for p in process.paths:
    pth = getattr(process,p)
    if "castorreco" in pth.moduleNames():
      pth.replace(process.castorreco, process.castorrecoORG*process.castorreco)

  process.ecalRecHitORG = process.ecalRecHit.clone()
  process.ecalRecHit = cms.EDProducer("EcalRHMixer",
         cleaningAlgo = cms.string("CaloCleanerAllCrossed"), # CaloCleanerMVA
         #cleaningAlgo = cms.string("CaloCleanerMVA"), 
         cleaningConfig = clConfig,
         todo = cms.VPSet(
              cms.PSet ( colZmumu = cms.InputTag("ecalRecHit","EcalRecHitsEB", inputProcess ), 
                         colTauTau = cms.InputTag("ecalRecHitORG","EcalRecHitsEB" )  ),

              cms.PSet ( colZmumu = cms.InputTag("ecalRecHit","EcalRecHitsEE", inputProcess  ), 
                         colTauTau = cms.InputTag("ecalRecHitORG","EcalRecHitsEE" )  )
         )
  )
  for p in process.paths:
    pth = getattr(process,p)
    if "ecalRecHit" in pth.moduleNames():
      pth.replace(process.ecalRecHit, process.ecalRecHitORG*process.ecalRecHit)



  process.hbherecoORG = process.hbhereco.clone()
  process.hbhereco = cms.EDProducer("HBHERHMixer",
         cleaningAlgo = cms.string("CaloCleanerAllCrossed"),
         cleaningConfig = clConfig,
         todo = 
           cms.VPSet(cms.PSet ( colZmumu = cms.InputTag( "hbhereco","", inputProcess  ), colTauTau = cms.InputTag("hbherecoORG","" )))
  )
  for p in process.paths:
    pth = getattr(process,p)
    if "hbhereco" in pth.moduleNames():
      pth.replace(process.hbhereco, process.hbherecoORG*process.hbhereco)

  # typedef CaloRecHitMixer< HFRecHit >   HFRHMixer;
  process.hfrecoORG = process.hfreco.clone()
  process.hfreco = cms.EDProducer("HFRHMixer",
         cleaningAlgo = cms.string("CaloCleanerAllCrossed"),
         cleaningConfig = clConfig,
         todo =
           cms.VPSet(cms.PSet ( colZmumu = cms.InputTag( "hfreco","", inputProcess  ), colTauTau = cms.InputTag("hfrecoORG","" )))
  )
  for p in process.paths:
    pth = getattr(process,p)
    if "hfreco" in pth.moduleNames():
      pth.replace(process.hfreco, process.hfrecoORG*process.hfreco)


  # typedef CaloRecHitMixer< HORecHit > HORHMixer;
  process.horecoORG = process.horeco.clone()
  process.horeco = cms.EDProducer("HORHMixer",
         cleaningAlgo = cms.string("CaloCleanerAllCrossed"),
         cleaningConfig = clConfig,
         todo =
           cms.VPSet(cms.PSet ( colZmumu = cms.InputTag( "horeco","", inputProcess  ), colTauTau = cms.InputTag("horecoORG","" )))
  )
  for p in process.paths:
    pth = getattr(process,p)
    if "horeco" in pth.moduleNames():
      pth.replace(process.horeco, process.horecoORG*process.horeco)



   


  # it should be the best solution to take the original beam spot for the
  # reconstruction of the new primary vertex
  # use the  one produced earlier, do not produce your own
  for s in process.sequences:
     seq =  getattr(process,s)
     seq.remove(process.offlineBeamSpot) 


  try:
  	process.metreco.remove(process.BeamHaloId)
  except:
  	pass

  try:
	  outputModule = process.output
  except:
    pass
  try:
	  outputModule = getattr(process,str(getattr(process,list(process.endpaths)[-1])))
  except:
    pass

  process.filterEmptyEv.src = cms.untracked.InputTag("generator","","EmbeddedRECO")


  try:
    process.schedule.remove(process.DQM_FEDIntegrity_v3)
  except:
    pass


  process.RECOSIMoutput.outputCommands.extend(['keep *_*_*_skimGoldenZmumu2'])

  # keep orginal collections, needed for PF2PAT - generalTracksORG, not sure for others 
  process.RECOSIMoutput.outputCommands.extend(['keep *_*ORG_*_*'])

  #xxx process.globalMuons.TrackerCollectionLabel = cms.InputTag("generalTracksORG")
  #xxx process.globalSETMuons.TrackerCollectionLabel = cms.InputTag("generalTracksORG")
  #print "TODO: add xcheck, that this is not changed"
  #process.muons.inputCollectionLabels = cms.VInputTag(cms.InputTag("generalTracksORG"), 
  #                             cms.InputTag("globalMuons"), 
  #                             cms.InputTag("standAloneMuons","UpdatedAtVtx"))


  skimEnabled = False
  if hasattr(process,"doZmumuSkim"):
      print "Enabling Zmumu skim"
      skimEnabled = True
      #process.load("TauAnalysis/Skimming/goldenZmmSelectionVBTFrelPFIsolation_cfi")

      
      cmssw_ver = os.environ["CMSSW_VERSION"]
      if cmssw_ver.find("CMSSW_4_2") != -1:
        print
        print "Using legacy version of Zmumu skim. Note, that muon isolation is disabled"
        print
        process.load("TauAnalysis/MCEmbeddingTools/ZmumuStandalonSelectionLegacy_cff")
      else:
        process.load("TauAnalysis/MCEmbeddingTools/ZmumuStandalonSelection_cff")
      process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")

      # we are allready selecting events from generation step, so following way is ok
      for path in process.paths:
          getattr(process,path)._seq = process.goldenZmumuSelectionSequence * getattr(process,path)._seq

      #process.options = cms.untracked.PSet(
      #  wantSummary = cms.untracked.bool(True)
      #)




  if not skimEnabled:
      print "Zmumu skim not enabled"


  print "# ######################################################################################"
  print "  Following parameters can be added before customize function "
  print "  call in order to controll process  customization: " 
  print "     process.doNotParse =  cms.PSet() # disables CL parsing for crab compat"
  print "     process.doZmumuSkim = cms.PSet() # adds Zmumu skimming before embedding is run"
  print "# ######################################################################################"


  return(process)
