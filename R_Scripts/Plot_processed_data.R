####################################################################################################
#          
#   View processed UniSpec-DC data
#   Author: Shawn P. Serbin
#
#
#	Info: Simple script file to load and plot processed data by directory
#
#
#
#  	--- Last updated:  03.16.2016 By Shawn P. Serbin <sserbin@bnl.gov>
####################################################################################################


#---------------- Close all devices and delete all variables. -------------------------------------#
rm(list=ls(all=TRUE))   # clear workspace
graphics.off()          # close any open graphics
closeAllConnections()   # close any open connections to files
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
### Input data directory
in.dir <- '~/Data/Projects/NGEE-Arctic/Tram_Spectra/20150715_processed/'
Project <- 'NGEE-Arctic'
Date <- '2015-07-15'
run <- '02_00_04'
spectra <- read.table(paste0(in.dir,Project,'_',Date,'__', run,'.csv'), header=FALSE,
                      skip=1,sep=",")
spectra[1:5,1:10]
spectra <- data.frame(spectra)
spectra.names <- c("Stop",paste0("Wave_",seq(302,1116,1)))
names(spectra) <- spectra.names
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
out.dir <- in.dir
if (! file.exists(out.dir)) dir.create(out.dir,recursive=TRUE)
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
## Subset spectral data to 
Start.wave <- 410
End.wave <- 980
inBands <- names(spectra)[match(paste0("Wave_",seq(Start.wave,End.wave,1)),names(spectra))]
spectra.sub <- droplevels(spectra[,inBands])
spec.info <- spectra[,1]

waves <- seq(Start.wave,End.wave,1)
plot(waves,spectra.sub[1,], type="l", col="black", lwd=3,ylim=c(0,0.5))
lines(waves,spectra.sub[spec.info==15,])
lines(waves,spectra.sub[spec.info==30,])
lines(waves,spectra.sub[spec.info==50,])
lines(waves,spectra.sub[spec.info==80,])
lines(waves,spectra.sub[spec.info==106,])
lines(waves,spectra.sub[spec.info==107,])
lines(waves,spectra.sub[spec.info==108,])
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
### Quick diagnostic plot
mn.refl <- colMeans(spectra.sub,na.rm=T)
min.refl <- sapply(spectra.sub,min,simplify=TRUE,na.rm=T)
max.refl <- sapply(spectra.sub,max,simplify=TRUE,na.rm=T)
sd.refl <- sapply(spectra.sub,sd,simplify=TRUE,na.rm=T)
mn.refl.upper <- mn.refl+sd.refl
mn.refl.lower <- mn.refl-sd.refl
spec.quant <- apply(spectra.sub,2,quantile,probs=c(0.05,0.95),na.rm=T)
reflCV <- (sd.refl/mn.refl)*100

cexaxis <- 1.5
cexlab <- 1.7
ylim <- 0.70
png(paste0(out.dir,'/',Project,'_',Date,'__',run,'_Spec_Summary.png'),width=2900, height =4000,res=400)
par(mfrow=c(2,1), mar=c(4.5,4.5,1.2,1.3), oma=c(0.1,0.1,0.1,0.1)) # B L T R
plot(waves,mn.refl,xlim=range(waves),ylim=c(0.01,ylim),cex=0.00001, col="white",xlab="",ylab="Reflectance (%)",
     cex.axis=cexaxis, cex.lab=cexlab)
polygon(c(waves ,rev(waves)),c(max.refl, rev(min.refl)),col="#99CC99",border=NA)
lines(waves,mn.refl,lwd=4)
lines(waves,spec.quant[1,],lty=2,lwd=1.6)
lines(waves,spec.quant[2,],lty=2,lwd=1.6)
#lines(waves,mn.refl.lower,lty=2,lwd=1.6)
#lines(waves,mn.refl.upper,lty=2,lwd=1.6)
lines(waves,max.refl, lty=3, lwd=1)
lines(waves,min.refl, lty=3, lwd=1)
legend("topleft",legend=c("Mean","95% CIs","Min / Max"),lty=c(1,2,3),
       lwd=c(2.2, 2.2, 2.2),bty="n", cex=1.7)
#legend("topleft",legend="All Spectra",cex=2,bty="n")
legend("bottomright",legend="(a)",cex=2,bty="n")
box(lwd=2.2)

# All spectra CV plot
plot(waves, as.vector(reflCV),xlim=range(waves),type="l",lwd=5, xlab="Wavelength (nm)", 
     ylab="Coefficient of Variation (%)",cex.axis=cexaxis, cex.lab=cexlab)
legend("topright",legend="(b)",cex=2,bty="n")
box(lwd=2.2)

dev.off()
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
### SVIs
NDVI <- (spectra.sub$Wave_800-spectra.sub$Wave_680)/(spectra.sub$Wave_800 + spectra.sub$Wave_680)
hist(NDVI)

# Water band index 970
WBI_970 <- spectra.sub$Wave_900/spectra.sub$Wave_970
hist(WBI_970)

# Photochemical reflectance index
PRI <- (spectra.sub$Wave_531-spectra.sub$Wave_570)/(spectra.sub$Wave_531+ spectra.sub$Wave_570)
PRI2 <- (PRI+1)/2
hist(PRI2)

# Leaf Chlorophyll Fluorescence ratio 2
#CF_740 <- spectra.sub$Wave_740/spectra.sub$Wave_800
#hist(CF_740)

# Lambda Red Edge & Red Edge position - 500nm:850nm
#Start.wave <- 550
#End.wave <- 850
#inBands <- names(spectra.sub)[match(paste0("Wave_",seq(Start.wave,End.wave,1)),names(spectra.sub))]
#spectra.sub2 <- droplevels(spectra.sub[,inBands])
#spec.sub.1diff <- t(apply(as.matrix(spectra.sub2),1,FUN=diff,1))
#plot(seq(550,850,1), spectra.sub2[1,],type="l")
#plot(seq(551,850,1),spec.sub.1diff[1,],type="l")
#lines(seq(551,850,1),spec.sub.1diff[2,])
#lines(seq(551,850,1),spec.sub.1diff[3,])

#waves <- seq(551,850,1)
#RE.pos <- apply(spec.sub.1diff,1,FUN=which.max)
#RE.pos <- waves[RE.pos]
#hist(RE.pos)

#--------------------------------------------------------------------------------------------------#


