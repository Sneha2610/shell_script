#!/bin/bash

###############################################################################
# DigiCert SSM OVA Signer 1.0 - 28-Jan-2022
#
# Use at your own risk. The use of this script is done at
# your own discretion and risk and with agreement that you will be
# solely responsible for any damage to your computer system or loss of data
# that results from such activities. You are solely responsible for adequate
# protection and backup of the data and equipment used in connection with any
# of the software, # and we will not be liable for any damages that you may
# suffer in connection with using, modifying or distributing any of this
# software. No advice or information, whether oral or written, obtained by you
# from us or from this website shall create any warranty for the software.
###############################################################################
###############################################################################
# Prerequisites & Dependencies:
# This script requires the following:
# 1) Prerequisites -
# The OVA\OVF Signer requires OpenSSL being configured for signing
# with Secure Software Manager. For instructions, see
# https://docs.digicert.com/en/digicert-one/secure-software-manager/signing-tools/openssl-configuration-and-signing.html
#
# 2) Dependencies -
# The OVA\OVF Signer requires Open Virtualization Format Tool (ovftool), which
# can be downloaded from VMware.
#
###############################################################################
###############################################################################
# Intructions:
# 1) Place this script and the OVA file in the same directory
# 2) Make the script executable: chmod +x DC1-OVA-Signer.sh
# 3) Follow screen prompts
###############################################################################
####################################################################
# Set Path to smtools-linux-x64/smpkcs11.so and OPENSSL_CONF
####################################################################

export OPENSSL_CONF='<path>/smtools-linux-x64/openssl_ssm.conf'

pathSMPKCS11='<path>/smtools-linux-x64/smpkcs11.so'

####################################################################
# Provide Public Key of Code Signing Certificate
####################################################################

cat > Code_Signing_Certificate.crt << EOF1
-----BEGIN CERTIFICATE-----

-----END CERTIFICATE-----
EOF1

####################################################################
# Enter the Key Pair Alias and ID of the Code Signing Certificate.
####################################################################
echo
read -p "Provide the Key Pair Alias of the Code Signing Certificate.: " keypairAlias
echo
read -p "Provide the Key Pair ID of the Code Signing Certificate.: " keypairID
echo
####################################################################
# Select the OVA or OVF File for Signing
####################################################################
#ovaInput=DSL.ova
echo
PS3="Select the OVA or OVF file to be digitally signed: "
files="$(ls -A .)"
select filename in ${files}; do echo "You selected ${filename}"; break; done
echo
####################################################################
# Base Filename
####################################################################
basename="${filename%.*}"
####################################################################
# Is file selected OVA or OVF?
####################################################################

if [[ $filename == *.ova ]]
then
  tar xvf $basename.ova

fi

####################################################################
# Create\Replace Manifest File
####################################################################
sleep 2
echo
echo
openssl sha256 *.vmdk *.ovf > $basename.mf
echo
echo "The $basename Manifest File has been created in the working directory."
echo
cat $basename.mf
echo

####################################################################
# Select Code Signing Private Key
####################################################################
echo
read -p "The Certificate(s) available for signing will now be listed. Do you want to continue? Y/N." -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

p11tool --provider=$pathSMPKCS11 --list-all-privkeys
echo
echo
read -p "Was the Certificate you intend to use for signing listed? Do you want to continue? Y/N." -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

####################################################################
# URL Encode the Key Pair ID
####################################################################

urlEncode=$(echo "$keypairID" | sed -e 's/%/%25/g' -e 's/ /%20/g' -e 's/3/%33/g' -e 's/4/%34/g' -e 's/5/%35/g' -e 's/6/%36/g' -e 's/7/%37/g' -e 's/8/%38/g' -e 's/9/%39/g' -e 's/c/%63/g' -e 's/d/%64/g' -e 's/e/%65/g' -e 's/f/%66/g' -e 's/g/%67/g' -e 's/h/%68/g' -e 's/i/%69/g' -e 's/j/%6A/g' -e 's/k/%6B/g' -e 's/l/%6C/g' -e 's/m/%6D/g' -e 's/n/%6E/g' -e 's/o/%6F/g' -e 's/p/%70/g' -e 's/q/%70/g' -e 's/r/%72/g' -e 's/s/%73/g' -e 's/t/%74/g' -e 's/u/%75/g' -e 's/v/%76/g' -e 's/w/%77/g' -e 's/x/%78/g' -e 's/y/%79/g' -e 's/z/%7A/g' -e 's/2/%32/g' -e 's/1/%31/g' -e 's/0/%30/g' -e 's/-/%2D/g' -e 's/b/%62/g' -e 's/a/%61/g')
echo
echo
echo "URL Encoded Key Pair ID:"
echo $urlEncode
echo
####################################################################
# Sign the Manifest File
####################################################################

openssl dgst -engine pkcs11 -keyform engine -sign "pkcs11:object=DigiCert%20PKCS%2311;manufacturer=DigiCert;serial=SS0123456789;token=Virtual%20PKCS%2311%20Token;id=$urlEncode;object=$keypairAlias;type=private" -sha256 -hex -out $basename.dgst $basename.mf

####################################################################
# Create the CERT File
####################################################################

cp $basename.dgst $basename.cert

cat Code_Signing_Certificate.crt >> $basename.cert
echo
echo "The file $basename.cert was created in the working directory:"
echo
cat $basename.cert
echo

####################################################################
# Validate the CERT File
####################################################################

ovftool $basename.ovf
echo
####################################################################
# Create the Signed OVA file or exit
####################################################################
echo
read -p "Do you want to create the OVA package or exit? Y=Create Package, N=Exit." -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

tar cvf $basename.ova --format=ustar $basename.ovf *.vmdk $basename.mf $basename.cert
echo
####################################################################
# Validate the CERT File
####################################################################

ovftool $basename.ova
echo
echo The signing of $basename.ova is complete.
####################################################################
# Cleanup
####################################################################

rm -f Code_Signing_Certificate.crt

exit 0
