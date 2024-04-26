Dropzone.options.uploadDropzone = {
    acceptedFiles: ['image/*'].join(','),
    method: 'PUT',
    thumbnailMethod: 'crop',
    resizeWidth: 500,
    resizeHeight: 500,
    autoProcessQueue: false, // Set autoProcessQueue to true to automatically upload files
    init: function () {
        var dropzone = this;

        this.on("addedfile", function () {
            if (this.files[1] != null) {
                this.removeFile(this.files[0]);
            }
        });

        // Handle form submission after all files have been uploaded
        this.on("queuecomplete", function () {
            document.getElementById('analyze-button').click(); // Trigger the click event of the analyze button
        });
    }
};
