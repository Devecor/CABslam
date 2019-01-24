% EXAMPLE 1
% Load image
function path = demoGist(path)
    if nargin == 0
        path = './test2Imgs/right/*/*.jpg';
    end

    ImgFile = dir(path);
    total_t = 0;
    for i = 1 : numel(ImgFile(:,1))
        clear img;
        img = imread(fullfile(ImgFile(i).folder,ImgFile(i).name));
        % fullfile(ImgFile(i).folder,ImgFile(i).name)
        % fprintf('dadadad\n')

        % Parameters:
        clear param
        % param.imageSize = [256 256]; % it works also with non-square images
        param.orientationsPerScale = [8 8 8 8];
        param.numberBlocks = 4;
        param.fc_prefilt = 4;

        % Computing gist requires 1) prefilter image, 2) filter image and collect
        % output energies
        savedir = strsplit(fullfile(ImgFile(i).name),'.');
        fprintf([fullfile('prosessing ', ImgFile(i).name, '... '), num2str(i), '/', num2str(numel(ImgFile(:,1)))]);
        tic
        [gist, param] = LMgist(img, '', param, fullfile('gistFeatures',savedir{1}));
        t_ = toc
        total_t = t_ + total_t
        fprintf(fullfile('done.\n saved in ','gistFeatures',savedir{1},'filegist.txt\n'));
        % showGist(gist, param)
        % pause(2)
    end
    exit
end

% Visualization
% figure
% subplot(121)
% imshow(img1)
% title('Input image')
% subplot(122)
% showGist(gist1, param)
% title('Descriptor')


% % EXAMPLE 2
% % Load image (this image is not square)
% img2 = imread('demo2.jpg');

% % Parameters:
% clear param 
% %param.imageSize. If we do not specify the image size, the function LMgist
% %   will use the current image size. If we specify a size, the function will
% %   resize and crop the input to match the specified size. This is better when
% %   trying to compute image similarities.
% param.orientationsPerScale = [8 8 8 8];
% param.numberBlocks = 4;
% param.fc_prefilt = 4;

% % Computing gist requires 1) prefilter image, 2) filter image and collect
% % output energies
% [gist2, param] = LMgist(img2, '', param, './gist2');

% % Visualization
% figure
% subplot(121)
% imshow(img2)
% title('Input image')
% subplot(122)
% showGist(gist2, param)
% title('Descriptor')

% input('press enter to exit:');
