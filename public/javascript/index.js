;$(function () {
    let hoverTimeCalculate = {};

    $('[data-cate]').on('click', function () {
        let $this = $(this)
        let cate = $this.data('cate')
        $.ajax(`/good_reads/${cate}`, {
            success(data) {
                let modal = $('#recommendation_modal').modal('show')
                modal.find('.modal-body').html(data)
                modal.find('.modal-title').html(`Recommendation for category ${cate}`)
            }
        })
    })

    $('[data-click]').on('click', function () {
        let $this = $(this).parents('[data-id]');
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let type = 'clickThrough';
        console.log(id, queryId)
        sendClick(id, queryId, $(this).data('click'))

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
        }, 15000)
    }, function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let time = new Date().getTime();
        if (hoverTimeCalculate[id] && time - hoverTimeCalculate[id] > 15000) {
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
            if (!queryId) {
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
        if (!queryId) {
            return
        }
        $.ajax('/hover', {
            method: 'post',
            data: {
                id, queryId, time
            }
        })
    }

    function sendClick(id, queryId, field) {
        if (!queryId) {
            return
        }
        $.ajax('/click', {
            method: 'post',
            data: {
                id, queryId, field
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