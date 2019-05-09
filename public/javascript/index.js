;(function () {
    let hoverTimeCalculate = {};

    $('[data-click]').on('click', function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryId');
        let type = 'clickThrough';
        sendClick(id, queryId)

    });
    $('[data-hover-monitor]').on('hover', function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryId');
        let time = new Date().getTime();
        hoverTimeCalculate[id] = time;
        setTimeout(() => {
            if (hoverTimeCalculate[id] === time) {
                sendHoverTime(id, queryId, time - hoverTimeCalculate[id])
            }
        }, 3000)
    }, function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryId');
        let time = new Date().getTime();
        if (hoverTimeCalculate[id] && time - hoverTimeCalculate[id] > 3000) {
            sendHoverTime(id, queryId, time - hoverTimeCalculate[id]);
            hoverTimeCalculate[id] = ''
        }
    });
    let dragStatus = false;
    $(document.body).mousedown(function () {
        dragStatus = true
    }).mouseup(function () {
        dragStatus = false
    });

    $('[data-drag-monitor]').on('mousemove', function () {
        if (!dragStatus) {
            return
        }
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryId');
        sendDrag(id, queryId)
    });

    let startTime = new Date().getTime()
    setInterval(() => {
        sendPageStayTime()
    }, 100000)

    function sendHoverTime(id, queryId) {

    }

    function sendClick(id, queryId) {

    }

    function sendDrag(id, queryId) {

    }

    function sendPageStayTime() {

    }
}());