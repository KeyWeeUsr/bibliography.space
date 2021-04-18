bibliography.space
==================

A simple website to list books with properties with
`even simpler API <https://bibliography.rest>`_.

How to contribute
*****************

.. |template| replace:: latest book template
.. _template: https://github.com/KeyWeeUsr/bibliography.space/blob/master/books/_template.yaml

.. |book-form| replace:: new book form
.. _book-form: https://github.com/KeyWeeUsr/bibliography.space/new/master/books

.. |new-uuid-duck| replace:: DuckDuckGo UUID
.. _new-uuid-duck: https://duckduckgo.com/?q=uuid

.. |new-uuid-ps| replace:: UUID in Powershell
.. _new-uuid-ps: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/new-guid

.. |new-uuid-unix| replace:: use ``uuidgen``

.. |sample-author| replace:: sample author
.. _sample-author: https://bibliography.space/935afa68-f27e-43af-b6a9-eb62bebdae20.html

.. |rest-check| replace:: ``/check/<uuid>`` API
.. _rest-check: https://bibliography.rest/check/<your-id-here>

GitHub
------

#. Open the |template|_
#. Go to the |book-form|_ and paste the template as is
#. Edit the template fields according to the legend at the top of the template
#. Pick a new UUID with |new-uuid-duck|_

   .. note::

      Repeat for all UUID fields if all of them are new. For example, if you
      are a new contributor and you are adding a new book with an author who's
      not listed in the DB, you need an UUID for you, the book item, the book
      title and the author.
      
      If you are adding a new book for an existing author, you need to pick
      the UUID of the author and use it in the template (|sample-author|_).

#. Verify the UUID is okay with |rest-check|_

   .. note:: ``404`` for *your* UUID means it's OK to use

#. Name the file as ``<author>--<title>.yaml``
#. Submit the form as a new pull request
#. Wait for review and merge
#. Enjoy :)

Git (CLI)
---------

#. Create your own `fork <https://guides.github.com/activities/forking/>`_
#. `Clone <https://www.git-scm.com/docs/git-clone>`_ the fork.
#. Create `a new branch <https://www.git-scm.com/docs/git-checkout>`_
   (``git checkout -b <branch>``)

#. Navigate to the repository's `books` folder
#. Generate a new UUIDs:

   * |new-uuid-duck|_
   * |new-uuid-ps|_
   * |new-uuid-unix|

#. Verify the UUID is okay with |rest-check|_

   .. note:: ``404`` for *your* UUID means it's OK to use

#. Copy the template to a file named ``<author>--<title>.yaml``
#. Fill the fields (GitHub note for reference)
#. `Commit <https://www.git-scm.com/docs/git-commit>`_ the new file
#. `Push <https://www.git-scm.com/docs/git-push>`_ the changes to your
   fork (``git push -u origin <branch>``)
#. Navigate to this repository
#. `Open a pull-request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>`_
#. Wait for review and merge
#. Enjoy :)
