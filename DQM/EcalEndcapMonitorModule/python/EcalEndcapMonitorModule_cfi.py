import FWCore.ParameterSet.Config as cms

ecalEndcapMonitorModule = cms.EDAnalyzer("EcalEndcapMonitorModule",
    EcalRawDataCollection = cms.InputTag("ecalEBunpacker"),
    EEDigiCollection = cms.InputTag("ecalEBunpacker","eeDigis"),
    EcalRecHitCollection = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
    EcalTrigPrimDigiCollection = cms.InputTag("ecalEBunpacker","EcalTriggerPrimitives"),
    prefixME = cms.untracked.string('EcalEndcap'),
    enableCleanup = cms.untracked.bool(False),
    mergeRuns = cms.untracked.bool(False),
    enableEventDisplay = cms.untracked.bool(False),
    runNumber = cms.untracked.int32(0),
    runType = cms.untracked.int32(-1),
    verbose = cms.untracked.bool(True),
    debug = cms.untracked.bool(False)
)

