Dropzone.options.uploadDropzone = {
    acceptedFiles: ['image/*'].join(','),
    method: 'PUT',
    thumbnailMethod: 'crop',
    resizeWidth: 500,
    resizeHeight: 500,
    autoProcessQueue: false,
    accept: function (file, done) {
        console.log("uploaded");
        done();
    },
    init: function () {
        this.on("addedfile", function () {
            if (this.files[1] != null) {
                this.removeFile(this.files[0]);
            }
        });
    }
};