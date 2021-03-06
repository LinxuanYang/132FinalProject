;$(function () {
    let hoverTimeCalculate = {};
    let hoverTimeFlag = {}
    let cate = ''
    $('body').on('click', '[data-cate]', function () {
        let $this = $(this)
        cate = $this.data('cate')
        $.ajax(`/good_reads/${cate}`, {
            success(data) {
                let modal = $('#recommendation_modal').modal('show')
                modal.find('.modal-body').html(data)
                modal.find('.modal-title').html(`Recommendation for category ${cate}`)
            }
        })
    }).on('click', '[data-jump]', function () {
        $.ajax(`/good_reads/${cate}`, {
            data: {pageNumber: $(this).data('jump')},
            success(data) {
                let modal = $('#recommendation_modal')
                modal.find('.modal-body').html(data)
                modal.find('.modal-title').html(`Recommendation for category ${cate}`)
            }
        })
    })

    $('body').on('click', '[data-click]', function () {
        let $this = $(this).parents('[data-id]');
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let type = 'clickThrough';
        sendClick(id, queryId, $(this).data('click'))

    });
    $('body').on('mouseenter', '[data-hover-monitor]', function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let time = new Date().getTime();
        hoverTimeCalculate[id] = time;
        setTimeout(() => {
            if (hoverTimeCalculate[id] === time) {
                sendHoverTime(id, queryId, new Date().getTime() - hoverTimeCalculate[id])
                hoverTimeCalculate[id] = new Date().getTime()
                hoverTimeFlag = true
            }
        }, 15000)
    }).on('mouseleave', '[data-hover-monitor]', function () {
        let $this = $(this);
        let id = $this.data('id');
        let queryId = $this.data('queryid');
        let time = new Date().getTime();
        if (hoverTimeFlag[id]) {
            sendHoverTime(id, queryId, time - hoverTimeCalculate[id]);
        }
        hoverTimeCalculate[id] = ''
        hoverTimeFlag[id] = false
    });
    let dragStatus = false;
    $('body').mousedown(function () {
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
        }, 1000
    )
    $('body').on('mousemove', '[data-drag-monitor]', function () {
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
        window.queryId && sendPageStayTime(queryId,)
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
    let time =new Date().getTime()
    function sendPageStayTime() {
        $.ajax('/page_stay', {
            method: 'post',
            data: {
                queryId: window.queryId, time: new Date().getTime() - time
            }
        })
    }

});