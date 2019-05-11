;$(function () {
    let hoverTimeCalculate = {};

    $('[data-click]').on('click', function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let type = 'clickThrough';
        sendClick(id, queryId)

    });
    $('[data-hover-monitor]').hover(function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let time = new Date().getTime();
        hoverTimeCalculate[id] = time;
        setTimeout(() => {
            if (hoverTimeCalculate[id] === time) {
                sendHoverTime(id, queryId, new Date().getTime() - hoverTimeCalculate[id])
            }
        }, 8000)
    }, function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let time = new Date().getTime();
        if (hoverTimeCalculate[id] && time - hoverTimeCalculate[id] > 8000) {
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

    let sendDrag = _.debounce((id, queryId) => {
        if(!queryId){
            return
        }
            $.ajax('/drag', {
                method: 'post',
                data: {
                    id, queryId
                }
            })
        }, 3000
    )
    $('[data-drag-monitor]').on('mousemove', function () {
        if (!dragStatus) {
            return
        }
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        sendDrag(id, queryId)
    });

    let startTime = new Date().getTime()
    setInterval(() => {
        window.queryId && sendPageStayTime()
    }, 100000)

    function sendHoverTime(id, queryId, time) {
        if(!queryId){
            return
        }
        $.ajax('/hover', {
            method: 'post',
            data: {
                id, queryId, time
            }
        })
    }

    function sendClick(id, queryId) {
        if(!queryId){
            return
        }
        $.ajax('/click', {
            method: 'post',
            data: {
                id, queryId
            }
        })
    }

    function sendPageStayTime() {
        $.ajax('/page_stay', {
            method: 'post',
            data: {
                queryId: window.queryId, time: new Date().getTime() - time
            }
        })
    }
});