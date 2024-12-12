% generate image and label file for paddle ocr rec train with 20 word a
% line with a dict contains 60 words.
clear all;
close all;
lastwarn('');
fileName='part60WordDict.txt';
textFileId=fopen(fileName,'r','n','UTF-8');
outFile='outPart60DictLabel20.txt';
outLabelId=fopen(outFile,'w','n','UTF-8');

outImagePath='./selfPart60DictRec20/images/';   %folder for out image
if exist(outImagePath,'dir')==0
    mkdir(outImagePath);
end
ziTi={'STKaiti','STFangsong','STSong','STXihei','STZhongsong'}; % almost support font
ziNum=size(ziTi,2);
wordNum=60;
oneLineWord=20; % word number per line, wordNum should be N*oneLineWord
m1=60;  % image height
m2=660; % image width
num=1;
sep=sprintf('%s\t','');
wordAll=[];
while(~feof(textFileId))
    for k=1:oneLineWord
        if(~feof(textFileId))
            temp=textscan(textFileId,'%s',1,'Delimiter','\n');
            textDisp=temp{1}{1};
            if(size(textDisp)~=1)
                t=1;
            end
            wordAll=[wordAll textDisp];
        end
    end
end

for k=1:70
    wordOrder=randperm(wordNum,wordNum);
    wordTemp=wordAll(wordOrder);
    for s=1:oneLineWord:wordNum
        wordOutTemp=wordTemp(s:s+oneLineWord-1);
        for t=1:ziNum
            randWord=randperm(oneLineWord,oneLineWord);
            wordOut=wordOutTemp(randWord);
            randColor=randperm(55,1);
            A = ones(m1,m2,3,'uint8')*(200+randColor);  %generate image with viarable background
            imFileName=['im' num2str(num) '.jpg'];
            A=insertText(A,[m2/2,m1/2],wordOut,'TextColor','black','FontSize',32,'Font',ziTi{t},'BoxColor' ,'white','AnchorPoint' ,'Center');    %
            textOut=['train_data/selfPart60DictRec20' imFileName sep wordOut];
            fprintf(outLabelId,'%s\n',textOut);
            imwrite(A,[outImagePath imFileName]); 
            num=num+1;
        end
    end
end
fclose(textFileId);
fclose(outLabelId);